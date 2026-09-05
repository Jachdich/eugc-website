<script lang="ts">
    import { get_people_names } from "./api";
    import { validate_float_string } from "./util";
    import PersonInput from "./PersonInput.svelte";
    import "./table.css";
    type Briefing = [number, Date, number, number];
    let briefings: Briefing[] = $state([]);

    async function get_briefings(): Promise<{ rows: any[] }> {
        let table = await fetch("/api/v1/list_briefings");
        let json = await table.json();
        return json;
    }

    let people_names: Map<number, string> = $state(new Map());
    get_people_names().then((pn) => people_names = pn);

    const make_briefing = (s: any) => [s[0], new Date(s[1] * 1000.0), ...s.slice(2)] as Briefing;
    get_briefings().then((ss) => briefings = ss["rows"].map((s) => make_briefing(s)));
    let new_person = $state(-1);
    let new_date = $state(new Date().toISOString().split("T")[0]);
    let new_score = $state("");

    function format_briefings(briefing: Briefing): string[] {
        return [
            briefing[0].toString(),
            briefing[1].toLocaleDateString(),
            people_names.get(briefing[2]),
            briefing[3].toString(),
        ];
    }

    function submit() {
        if (new_person < 0) return;
        if (new_score == "") return;
        const timestamp = +(new Date(new_date)) / 1000;
        const packet = {
            date: timestamp,
            person: new_person,
            score: Number.parseFloat(new_score),
        };

        fetch("/api/v1/add-briefing", {
            method: "POST",
            body: JSON.stringify(packet),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        }).then((response) => {
            if (response.status == 200) {
                response.json().then((j) => 
                    briefings = [make_briefing(j), ...briefings]
                );
                new_person = -1;
                new_score = "";
            } else {
                alert("Failed to add briefing: " + response.status);
            }
        });
    }

    function validate_cell_value(event: Event & {currentTarget: EventTarget & HTMLInputElement}) {
        let value = event.currentTarget.value;
        let input = event.currentTarget;
        input.value = validate_float_string(value);
    }

</script>

<table>

    <thead>
        <tr>
            <th>ID</th>
            <th>Date</th>
            <th>Person</th>
            <th>Score</th>
        </tr>
    </thead>

    <tbody>
        <tr class="odd-row">
            <td><button type="button" onclick={submit}>+</button></td>
            <td><input type="date" bind:value={new_date} /></td>
            <td><PersonInput people={people_names} bind:person={new_person}/></td>
            <td><input type="text" style="width: 48px;" bind:value={new_score} oninput={(e) => validate_cell_value(e)}/></td>
    
        </tr>
        {#each briefings as briefing, row_index}
            <tr class="{row_index % 2 == 0 ? 'even-row' : 'odd-row'}">
                {#each format_briefings(briefing) as col}
                    <td>{col}</td>
                {/each}
            </tr>
        {/each}
    </tbody>

</table>
