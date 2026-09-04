
<script lang="ts">

    import PersonInput from "./PersonInput.svelte";
    import { get_people_names } from "./api";


    interface Day {
        date: Date,
        instruct: number[],
        transport: number[],
        supervise: number[],
        notes: string | undefined,
    }
    let days: Day[] = $state([]);

    let people: Map<number, string> = $state(new Map());

    get_people_names().then((p) => {
        people = p;
        days = [
            {date: new Date(2026, 0, 2), instruct: [1, 2], transport: [4, 5, 6], supervise: [10], notes: undefined },
            {date: new Date(2026, 0, 3), instruct: [8], transport: [], supervise: [1], notes: undefined },
            {date: new Date(2026, 0, 4), instruct: [], transport: [30], supervise: [18, 19, 20], notes: "Long kinda note because something serious happened at the airfield that caused some significant problems for EUGC including the agreement" },
            {date: new Date(2026, 0, 9), instruct: [], transport: [6], supervise: [], notes: undefined },
            {date: new Date(2026, 0, 10), instruct: [16], transport: [], supervise: [], notes: "Cancelled due to weather" },
            {date: new Date(2026, 0, 11), instruct: [17], transport: [], supervise: [], notes: undefined },
        ];
    });
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
                <td><PersonInput bind:person={days[day_idx].transport[r_idx]} {people} onchange={() => { if (days[day_idx].transport[r_idx] < 0) { days[day_idx].transport.splice(r_idx, 1); } }} /></td>
            {/each}
            <td><button onclick={() => { day.transport.push(-1); }}>+</button></td>
        </tr>
        <tr>
            <td>Supervising</td>
            {#each day.supervise as superviseor, r_idx}
                <td><PersonInput bind:person={days[day_idx].supervise[r_idx]} {people} onchange={() => { if (days[day_idx].supervise[r_idx] < 0) { days[day_idx].supervise.splice(r_idx, 1); } }} /></td>
            {/each}
            <td><button onclick={() => { day.supervise.push(-1); }}>+</button></td>
        </tr>
        <tr>
            <td>Notes</td>
            <td colspan="10">{day.notes === undefined ? "None" : day.notes}</td>
        </tr>
    </tbody></table>
{/each}

