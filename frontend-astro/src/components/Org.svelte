<script lang="ts">

    import PersonInput from "./PersonInput.svelte";
    import { validate_float_string } from "./util";
    import { get_people_names } from "./api";


    interface Day {
        date: Date,
        instruct: number[],
        transport: [number, number][],
        supervise: number[],
        attend: number[],
        notes: string | undefined,
    }
    let days: Day[] = $state([]);

    export async function get_flying_days(): Promise<Array<Day>> {
        let table = await fetch("/api/v1/get-flying-days");
        let json = await table.json();
        return json["rows"].map((day: any) => { return {date: new Date(day["date"] * 1000), attend: day["attend"], instruct: day["instruct"], transport: day["transport"], supervise: day["supervise"], notes: day["notes"]};});
    }

    let people: Map<number, string> = $state(new Map());

    get_people_names().then((p) => {
        people = p;
    });
    get_flying_days().then(fd => {
        days = fd;
    });

    function validate_number(event: Event & {currentTarget: EventTarget & HTMLInputElement}, day: number, transport_idx: number) {
        let value = event.currentTarget.value;
        let input = event.currentTarget;
        input.value = validate_float_string(value);
        days[day].transport[transport_idx][1] = input.value === "" ? 0 : Number.parseInt(input.value);
    }
    // const max = 3;
</script>

<!--
<table>
    <thead>
        <tr>
            <th></th>
            <th colspan="3">Instructing</th>
            <th colspan="3">Transporting</th>
            <th colspan="3">Supervising</th>
        </tr>
    </thead>
    <tbody>
        {#each days as day}
            <tr>
                <th>{`${day.date.toDateString()}`}</th>
                {#each day.instruct as instructor}
                    <td><PersonInput person={instructor} people={people} onchange={() => undefined} /></td>
                {/each}
                {#each new Array(max - day.instruct.length).values() as _}
                    <td></td>
                {/each}
                {#each day.supervise as supervisor}
                    <td><PersonInput person={supervisor} people={people} onchange={() => undefined} /></td>
                {/each}
                {#each new Array(max - day.supervise.length).values() as _}
                    <td></td>
                {/each}
                {#each day.transport as transportor}
                    <td><PersonInput person={transportor} people={people} onchange={() => undefined} /></td>
                {/each}
                {#each new Array(max - day.transport.length).values() as _}
                    <td></td>
                {/each}
            </tr>
        {/each}
    </tbody>
</table>
<style>

    table {
        border-collapse: collapse;
        border: 1px solid black;
        margin: 3px;
        font-size: 12px;
    }

    th, td {
        border: 1px solid black;
        min-width: 64px;
    }

</style>
-->

{#each days as day, day_idx}
    <h3>{day.date.toDateString()}</h3>
    <table><tbody>
        <tr>
            <td>Instructing</td>
            {#each day.instruct as instructor, r_idx}
                <td><PersonInput bind:person={days[day_idx].instruct[r_idx]} {people} onchange={() => { if (days[day_idx].instruct[r_idx] < 0) { days[day_idx].instruct.splice(r_idx, 1); } }} /></td>
            {/each}
            <td><button onclick={() => { day.instruct.push(-1); }}>+</button></td>
        </tr>
        <tr>
            <td>Transporting</td>
            {#each day.transport as transportor, r_idx}
                <td><PersonInput bind:person={days[day_idx].transport[r_idx][0]} {people} onchange={() => { if (days[day_idx].transport[r_idx][0] < 0) { days[day_idx].transport.splice(r_idx, 1); } }} /></td>
            {/each}
            <td><button onclick={() => { day.transport.push([-1, 0]); }}>+</button></td>
        </tr>
        <tr>
            <td>Spaces</td>
            {#each day.transport as transportor, r_idx}
                <td><input type="text" style="width: 48px;" value="{transportor[1]}" oninput={(e) => validate_number(e, day_idx, r_idx)} /></td>
            {/each}
        </tr>
        <tr>
            <td>Supervising</td>
            {#each day.supervise as superviseor, r_idx}
                <td><PersonInput bind:person={days[day_idx].supervise[r_idx]} {people} onchange={() => { if (days[day_idx].supervise[r_idx] < 0) { days[day_idx].supervise.splice(r_idx, 1); } }} /></td>
            {/each}
            <td><button onclick={() => { day.supervise.push(-1); }}>+</button></td>
        </tr>
        <tr>
            <td>Attending</td>
            {#each day.attend as attendor, r_idx}
                <td><PersonInput bind:person={days[day_idx].attend[r_idx]} {people} onchange={() => { if (days[day_idx].attend[r_idx] < 0) { days[day_idx].attend.splice(r_idx, 1); } }} /></td>
            {/each}
            <td><button onclick={() => { day.attend.push(-1); }}>+</button></td>
        </tr>
        <tr><td>Attendance</td><td>{day.attend.length}/{day.transport.reduce((a, b) => a + b[1], 0)}</td></tr>
        <tr>
            <td>Notes</td>
            <td style="width: 0px;" colspan="10">{day.notes === undefined ? "None" : day.notes}</td>
        </tr>
    </tbody></table>
{/each}

