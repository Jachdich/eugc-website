<script lang="ts">

    import { validate_float_string } from "./util";

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
        AvailSun: 13,
        DaySinceFly: 14,
        SignupSinceFly: 15,
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
                row[12], row[13]
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
            value = validate_float_string(value);
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
        let updated = true;
        let original = table[row].cells[column];
        if (column == RowIx.ENumber) {
            table[row].cells[RowIx.ENumber] = Number.parseInt(value.substring(1));
        } else if (column == RowIx.Name) {
            table[row].cells[RowIx.Name] = value;
        } else if (column == RowIx.Notes) {
            table[row].cells[RowIx.Notes] = value == "" ? null : value;
        } else if (column == RowIx.Emails || column == RowIx.Phones) {
            table[row].cells[column] = value.split(",").map((i) => i.trim());
        } else if (column == RowIx.Keenness) {
            table[row].cells[column] = value == "" ? 0 : Number.parseFloat(value);
        } else {
            updated = false;
        }

        if (updated) {
            const packet = {
                id: table[row].cells[RowIx.Id], col: column, new_value: table[row].cells[column]
            };
            fetch("/api/v1/update-cell", {
              method: "POST",
              body: JSON.stringify(packet),
              headers: {
                "Content-type": "application/json; charset=UTF-8"
              }
            }).then((response) => {
                if (response.status == 200) {

                } else {
                    alert("Failed to set cell value: " + response.status);
                    table[row].cells[column] = original;
                }
            });
        }

    }
    
    interface ColumnInfo {
        name: string,
        width: number,
        readonly: boolean,
        idx: number,
    }
    
    const COL_INFOS: ColumnInfo[] = [
        {idx: RowIx.Id,            name: "ID", width: 24, readonly: true},
        {idx: RowIx.Name,          name: "Name", width: 150, readonly: false},
        {idx: RowIx.ENumber,       name: "Exxx", width: 40, readonly: false},
        {idx: RowIx.NumSignups,    name: "Signups", width: 40, readonly: true},
        {idx: RowIx.NumFlyingDays, name: "Flies", width: 40, readonly: true},
        {idx: RowIx.Keenness,      name: "Keenness", width: 30, readonly: false},
        {idx: RowIx.BriefingScore, name: "Score", width: 30, readonly: true},
        {idx: RowIx.DaySinceFly,   name: "DSLF", width: 20, readonly: true},
        {idx: RowIx.SignupSinceFly,name: "SSLF", width: 20, readonly: true},
        {idx: RowIx.AvailFri,      name: "Fri", width: 20, readonly: false},
        {idx: RowIx.AvailSat,      name: "Sat", width: 20, readonly: false},
        {idx: RowIx.AvailSun,      name: "Sun", width: 20, readonly: false},
        {idx: RowIx.BriefingDate,  name: "Recency", width: 80, readonly: true},
        {idx: RowIx.Emails,        name: "Email", width: 140, readonly: false},
        {idx: RowIx.Phones,        name: "Phone", width: 110, readonly: false},
        {idx: RowIx.Notes,         name: "Notes", width: 250, readonly: false},
    ]

    function input_keypress(e: KeyboardEvent, row_index: number, col_index: number) {
        if (e.key === "Enter") {
            // document.activeElement.blur();
            table_filtered[row_index + 1].inputs[col_index].focus();
            // table_filtered[row_index].inputs[col_index].blur();
        }
    }

    function to_string_empty_if_null(value: string | number | null): string {
        if (value === null) return "";
        return value.toString();
    }

    function serialise_cell(row: Row, column: number): [string, string] {
        switch (column) {
            case RowIx.Id:             return [row.cells[column].toString(), ""];
            case RowIx.Name:           return [row.cells[column], ""];
            case RowIx.Notes: {
                let notes = row.cells[column];
                return [notes === null ? "" : notes, ""];
            }
            case RowIx.ENumber:        return [row.cells[RowIx.ENumber] === null ? "" : "E" + row.cells[RowIx.ENumber].toString(), ""];
            case RowIx.Emails:         return [row.cells[column].join(","), ""];
            case RowIx.Phones:         return [row.cells[column].join(","), ""];
            case RowIx.NumSignups:     return [row.cells[column].toString(), ""];
            case RowIx.NumFlyingDays:  return [row.cells[column].toString(), ""];
            case RowIx.BriefingScore: {
                let score = row.cells[column];
                let cls = "";
                if (score !== null) {
                    if (score <= 0) {
                        cls = "black";
                    } else if (score < 2) {
                        cls = "red";
                    } else if (score < 3) {
                        cls = "amber";
                    } else if (score < 4) {
                        cls = "green";
                    }
                }
                return [score === null ? "" : score.toString(), cls];
            }
            case RowIx.Keenness: {
                let score = row.cells[column];
                return [score === null ? "" : score.toString(), ""];
            }
            case RowIx.BriefingDate: {
                let date_str = "";
                const briefing_date = row.cells[RowIx.BriefingDate];
                let cls = "";
                if (briefing_date !== null) {
                    const date = new Date(briefing_date * 1000);
                    date_str = date.toLocaleDateString();
                    let ms_since = (+new Date()) - briefing_date * 1000;
                    let s_since = ms_since / 1000;
                    let days_since = s_since / 60 / 60 / 24;
                    if (days_since < 30) {
                        cls = "green";
                    } else if (days_since < 60) {
                        cls = "yellow";
                    } else if (days_since < 90) {
                        cls = "amber";
                    } else {
                        cls = "red";
                    }
                }
                return [date_str, cls];
            }
            case RowIx.AvailFri:       return [to_string_empty_if_null(row.cells[column]), ""];
            case RowIx.AvailSat:       return [to_string_empty_if_null(row.cells[column]), ""];
            case RowIx.AvailSun:       return [to_string_empty_if_null(row.cells[column]), ""];
            case RowIx.DaySinceFly:    return [to_string_empty_if_null(row.cells[column]), ""];
            case RowIx.SignupSinceFly: return [to_string_empty_if_null(row.cells[column]), ""];
        }
        return ["Unknown Column", ""];
    }
    
</script>

<input type="checkbox" id="avail" onclick={filter_avail}/>
<label for="avail">Available</label>

<div id="table">
    <table>
        <thead>
            <tr>
                {#each COL_INFOS as info}
                    <th><button style="min-width: {info.width}px;" onclick={() => sort(info.idx)}>{info.name}</button></th>
                {/each}
            </tr>
        </thead>
        <tbody>
            {#each table_filtered as row, row_index}
                <tr class="{row_index % 2 == 0 ? 'even-row' : 'odd-row'}">
                    {#each COL_INFOS as info}
                        {@const [serialised_value, style_class] = serialise_cell(row, info.idx)}
                        <td class={style_class}>
                            <input
                                class="item"
                                value={serialised_value}
                                disabled={info.readonly}
                                onblur={(e) => update_cell_value(e, serialised_value, row_index, info.idx)}
                                onkeypress={(e) => input_keypress(e, row_index, info.idx)}
                                bind:this={row.inputs[info.idx]}
                                oninput={(e) => validate_cell_value(e, info.idx)}
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
        color: #222288;
    }

    input:disabled {
        color: #222222;
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

    .red {
        background-color: #ff8f8f;
    }

    .amber {
        background-color: #ffdf8f;
    }
    .yellow {
        background-color: #ffff8f;
    }
    .green {
        background-color: #8fff8f;
    }
    .black {
        background-color: #888888;
    }

</style>
