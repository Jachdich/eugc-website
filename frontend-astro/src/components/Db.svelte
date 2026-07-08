<script lang="ts">

    const RowIx = {
        Id: 0,
        Name: 1,
        Notes: 2,
        ENumber: 3,
        Emails: 4,
        Phones: 5,
        NumSignups: 6,
        NumFlyingDays: 7,
        Keenness: 8,
        BriefingScore: 9,
        BriefingDate: 10,
        AvailFri: 11,
        AvailSat: 12,
        AvailSun: 13
    } as const;

    const MONDAY   = 0b0000001;
    const TUESDAY  = 0b0000010;
    const WEDNESDAY= 0b0000100;
    const THURSDAY = 0b0001000;
    const FRIDAY   = 0b0010000;
    const SATURDAY = 0b0100000;
    const SUNDAY   = 0b1000000;
    

    interface Row {
        cells: [
            number,
            string,
            string | null,
            number,
            string[],
            string[],
            number,
            number,
            number | null,
            number | null,
            number | null,
            number | null,
            number | null,
            number | null,
        ],
        inputs: HTMLInputElement[],
    }

    let table: Row[] = $state([]);
    let table_filtered: Row[] = $state([]);
    get_people().then((t: { rows: any[] }) => {
        table = t.rows.map((row: any[]) => { return {
            cells: [
                ...row.slice(0, 11),
                row[11] & FRIDAY ? 0 : null,
                row[11] & SATURDAY ? 0 : null,
                row[11] & SUNDAY ? 0 : null,
            ] as any,
            inputs: [],
        }});
        table_filtered = table;
    });
    async function get_people(): Promise<{ rows: any[] }> {
        let table = await fetch("/api/v1/list_people");
        let json = await table.json();
        return json;
    }

    function filter_avail(event: any) {
        if (event.target.checked) {
            table_filtered = table.filter((row) =>
                row.cells[RowIx.AvailSat] != null ||
                row.cells[RowIx.AvailSun] != null ||
                row.cells[RowIx.AvailFri] != null
            );
        } else {
            table_filtered = table;
        }
    }

    let last_sort: number | undefined;
    let sort_direction: "Ascending" | "Descending" = "Descending";
    
    function sort(column: number) {
        if (last_sort === column) {
            if (sort_direction == "Ascending") {
                sort_direction = "Descending";
            } else {
                sort_direction = "Ascending";
            }
        }
        table_filtered = table_filtered.toSorted((a, b) => {
            let av, bv;
            if (sort_direction == "Descending") {
                av = a.cells[column];
                bv = b.cells[column];
                if (av == null) return 1;
                if (bv == null) return -1;
            } else {
                bv = a.cells[column];
                av = b.cells[column];
                if (av == null) return -1;
                if (bv == null) return 1;
            }
            if (typeof av == "string" && typeof bv == "string") {
                return av.localeCompare(bv);
            } else if (typeof av == "number" && typeof bv == "number") {
                return av - bv;
            }
            return 0;
        });

        last_sort = column;
    }

    function validate_cell_value(event: Event & {currentTarget: EventTarget & HTMLInputElement}, column: number) {
        let value = event.currentTarget.value;
        let input = event.currentTarget;
        if (column == RowIx.Name || column == RowIx.Notes) {
            return; // string | null is never false
        }
        if (column == RowIx.ENumber) {
            if (value.length == 0 || value[0] != "E") {
                value = "E" + value;
            }
            let number = value.substring(1);
            number = number.replace(/[^0-9]/g, '');
            if (number.length == 0) {
                number = "0";
            }
            if (number.length > 1 && number[0] == "0") {
                number = number.substring(1);
            }
            value = "E" + number;
        }

        if (column == RowIx.Emails || column == RowIx.Phones) {
            return;
        }

        // if (column == 6 || column == 7) {
        //     value = value.replace(/[^0-9]/g, '');
        // }

        if (column == RowIx.Keenness) {
            let has_minus = value[0] == "-";
            if (has_minus) {
                value = value.substring(1);
            }
            let value_pieces = value.split(".");
            if (value_pieces.length == 1) {
                value = value_pieces[0];
            } else if (value_pieces.length == 2) {
                value = value_pieces.join(".");
            } else {
                value = value_pieces[0] + "." + value_pieces[1] + value_pieces.slice(2).join("");
            }
            value = value.replace(/[^0-9\.]/g, '');
            if (has_minus) {
                value = "-" + value;
            }
        }

        input.value = value;
    }

    function update_cell_value(e: any, old: string, row_index: number, col_index: number) {
        if (e.target.value !== old.toString()) {
            const target_id = table_filtered[row_index].cells[RowIx.Id];
            for (let i = 0; i < table.length; i++) {
                if (table[i].cells[RowIx.Id] == target_id) {
                    parse_cell_value(e.target.value, col_index, i);
                    break;
                }
            }
        }
    }

    function parse_cell_value(value: string, column: number, row: number) {
        if (column == RowIx.ENumber) {
            table[row].cells[RowIx.ENumber] = Number.parseInt(value.substring(1));
        }

        if (column == RowIx.Name) {
            table[row].cells[RowIx.Name] = value;
        }
        if (column == RowIx.Notes) {
            table[row].cells[RowIx.Notes] = value == "" ? null : value;
        }

        if (column == RowIx.Emails || column == RowIx.Phones) {
            table[row].cells[column] = value.split(",").map((i) => i.trim());
        }

        // if (column == RowIx.NumSignups || column == RowIx.NumFlyingDays) {
        //     table[row].cells[column] = value == "" ? 0 : Number.parseInt(value);
        // }
        if (column == RowIx.Keenness) {
            table[row].cells[column] = value == "" ? 0 : Number.parseFloat(value);
        }

    }
    
    interface ColumnInfo {
        name: string,
        width: number,
        readonly: boolean,
    }
    
    const COL_INFOS: ColumnInfo[] = [
        {name: "ID", width: 24, readonly: true},
        {name: "Name", width: 150, readonly: false},
        {name: "Notes", width: 160, readonly: false},
        {name: "E number", width: 40, readonly: false},
        {name: "Email", width: 140, readonly: false},
        {name: "Phone", width: 130, readonly: false},
        {name: "Signups", width: 40, readonly: true},
        {name: "Flying days", width: 40, readonly: true},
        {name: "Keenness", width: 30, readonly: false},
        {name: "Briefing score", width: 30, readonly: true},
        {name: "Recency", width: 80, readonly: true},
        {name: "Fri", width: 20, readonly: false},
        {name: "Sat", width: 20, readonly: false},
        {name: "Sun", width: 20, readonly: false},
    ]

    function input_keypress(e: KeyboardEvent, row_index: number, col_index: number) {
        if (e.key === "Enter") {
            // document.activeElement.blur();
            table_filtered[row_index + 1].inputs[col_index].focus();
            // table_filtered[row_index].inputs[col_index].blur();
        }
    }

    function get_values(row: Row): string[] {
        let date_str = "";
        const briefing_date = row.cells[RowIx.BriefingDate];
        if (briefing_date !== null) {
            const date = new Date(briefing_date * 1000);
            const d = date.getDate();
            const m = date.getMonth();
            const y = date.getFullYear();
            date_str = `${d}/${m}/${y}`;
        }
        let keenness = row.cells[RowIx.Keenness];
        let briefing_score = row.cells[RowIx.BriefingScore];
        let notes = row.cells[RowIx.Notes];
        let afr = row.cells[RowIx.AvailFri];
        let asa = row.cells[RowIx.AvailSat];
        let asu = row.cells[RowIx.AvailSun];
        return [
            row.cells[RowIx.Id].toString(),
            row.cells[RowIx.Name],
            notes === null ? "" : notes,
            row.cells[RowIx.ENumber] === null ? "" : "E" + row.cells[RowIx.ENumber].toString(),
            row.cells[4].join(", "),
            row.cells[5].join(", "),
            row.cells[6].toString(),
            row.cells[7].toString(),
            keenness === null ? "" : keenness.toString(),
            briefing_score === null ? "" : briefing_score.toString(),
            date_str,
            afr === null ? "" : afr.toString(),
            asa === null ? "" : asa.toString(),
            asu === null ? "" : asu.toString(),
        ]
    }
    
</script>

<input type="checkbox" id="avail" onclick={filter_avail}/>
<label for="avail">Available</label>

<div id="table">
    <table>
        <thead>
            <tr>
                {#each COL_INFOS as info, idx}
                    <th><button style="min-width: {info.width}px;" onclick={() => sort(idx)}>{info.name}</button></th>
                {/each}
            </tr>
        </thead>
        <tbody>
            {#each table_filtered as row, row_index}
                <tr class="{row_index % 2 == 0 ? 'even-row' : 'odd-row'}">
                    {#each get_values(row) as item, col_index}
                        <td>
                            <input
                                class="item"
                                value={item}
                                disabled={COL_INFOS[col_index].readonly}
                                onblur={(e) => update_cell_value(e, item, row_index, col_index)}
                                onkeypress={(e) => input_keypress(e, row_index, col_index)}
                                bind:this={row.inputs[col_index]}
                                oninput={(e) => validate_cell_value(e, col_index)}
                            />
                        </td>
                    {/each}
                </tr>
            {/each}
        </tbody>
    </table>
</div>

<style>

    table {
        border-collapse: collapse;
        border: 1px solid black;
        margin: 3px;
        font-size: 12px;
    }

    th, td {
        border: 1px solid black;
    }
    input {
        background-color: inherit;
    }

    .even-row {
        background-color: #ededed;
    }
    .odd-row {
        background-color: #ffffff;
    }

    .item {
        overflow-x: hidden;
        height: 14px;
        white-space: nowrap;
        border: none;
        width: 0;
        min-width: 100%;
        padding: 0px;
        margin: 0px;
    }

</style>
