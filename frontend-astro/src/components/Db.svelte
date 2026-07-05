<script lang="ts">

    interface Row {
        id: number,
        name: string,
        notes: string | null,
        e_number: number,
        emails: string[],
        phones: string[],
        num_signups: number,
        num_flying_days: number,
        keenness: number | null,
        briefing_score: number | null,
        briefing_date: number | null,
        availability: number,
        inputs: HTMLInputElement[],
    }

    let table: Row[] = $state([]);
    let table_filtered: Row[] = $state([]);
    let table_head: string[] = $state([]);
    get_people().then((t) => {
        table = t["rows"].map((row: any) => { return {
            id: row[0],
            name: row[1],
            notes: row[2],
            e_number: row[3],
            emails: row[4],
            phones: row[5],
            num_signups: row[6],
            num_flying_days: row[7],
            keenness: row[8],
            briefing_score: row[9],
            briefing_date: row[10],
            availability: row[11],
            inputs: [],
        }});
        table_filtered = table;
        table_head = Object.keys(table[0]);
    });
    async function get_people(): Promise<Map<string, string>[]> {
        let table = await fetch("/api/v1/list_people");
        let json = await table.json();
        return json;
    }

    function filter_avail(event: any) {
        if (event.target.checked) {
            table_filtered = table.filter((row) => row.availability != 0);
        } else {
            table_filtered = table;
        }
    }

    let last_sort: string | undefined;
    let sort_direction: "Ascending" | "Descending" = "Descending";
    
    function sort(item: string) {
        if (last_sort === item) {
            if (sort_direction == "Ascending") {
                sort_direction = "Descending";
            } else {
                sort_direction = "Ascending";
            }
        }
        table_filtered = table_filtered.toSorted((a, b) => {
            let av, bv;
            if (sort_direction == "Descending") {
                av = a[item];
                bv = b[item];
            } else {
                bv = a[item];
                av = b[item];
            }
            if (typeof(av) == "string") {
                return av.localeCompare(bv);
            } else {
                return av - bv;
            }
        });

        last_sort = item;
    }

    function update_cell_value(e: any, old: string) {
        if (e.target.value !== old.toString()) {
            console.log(e.target.value);
        }
    }

    function get_real_name(key: string): string {
        return {
            id: "ID",
            name: "Name",
            notes: "Notes",
            e_number: "E number",
            emails: "Email",
            phones: "Phone",
            num_signups: "Signups",
            num_flying_days: "Flying days",
            keenness: "Keenness",
            briefing_score: "Briefing score",
            briefing_date: "Recency",
            availability: "Availability",
        }[key] as string;
    }
    function get_col_size(key: string): number {
        return {
            id: 24,
            name: 150,
            notes: 160,
            e_number: 40,
            emails: 140,
            phones: 130,
            num_signups: 40,
            num_flying_days: 40,
            keenness: 30,
            briefing_score: 30,
            briefing_date: 80,
            availability: 40,
        }[key] as number;
    }

    function input_keypress(e: KeyboardEvent, row_index: number, col_index: number) {
        if (e.key === "Enter") {
            // document.activeElement.blur();
            table_filtered[row_index + 1].inputs[col_index].focus();
            // table_filtered[row_index].inputs[col_index].blur();
        }
    }

    function get_values(row: Row): any[] {
        let date_str = "";
        if (row.briefing_date !== null) {
            const date = new Date(row.briefing_date);
            const d = date.getDate();
            const m = date.getMonth();
            const y = date.getFullYear();
            date_str = `${d}/${m}/${y}`;
        }
        return [
            row.id.toString(),
            row.name,
            row.notes === null ? "" : row.notes,
            row.e_number === null ? "" : "E" + row.e_number.toString(),
            row.emails.join(", "),
            row.phones.join(", "),
            row.num_signups.toString(),
            row.num_flying_days.toString(),
            row.keenness === null ? "" : row.keenness.toString(),
            row.briefing_score === null ? "" : row.briefing_score.toString(),
            date_str,
            row.availability.toString(),
        ]
    }
    
</script>

<input type="checkbox" id="avail" onclick={filter_avail}/>
<label for="avail">Available</label>

<div id="table">
    <table>
        <thead>
            <tr>
                {#each table_head as item}
                    <th><button style="min-width: {get_col_size(item)}px;" onclick={() => sort(item)}>{get_real_name(item)}</button></th>
                {/each}
            </tr>
        </thead>
        <tbody>
            {#each table_filtered as row, row_index}
                <tr>
                    {#each get_values(row) as item, index}
                        <td>
                            <input
                                class="item"
                                value={item}
                                onblur={(e) => update_cell_value(e, item)}
                                onkeypress={(e) => input_keypress(e, row_index, index)}
                                bind:this={row.inputs[index]}
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
