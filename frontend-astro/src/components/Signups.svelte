<script lang="ts">
    import { FRIDAY, get_people_names, SATURDAY, SUNDAY } from "./api";
    import "./table.css";
    type Signup = [number, number, Date, boolean, boolean, number, boolean, string];
    let signups: Signup[] = $state([]);

    async function get_signups(): Promise<{ rows: any[] }> {
        let table = await fetch("/api/v1/list_signups");
        let json = await table.json();
        return json;
    }

    let people_names: Map<number, string> = $state(new Map());
    get_people_names().then((pn) => people_names = pn);

    get_signups().then((ss) => signups = ss["rows"].map((s) => [s[0], s[1], new Date(s[2] * 1000.0), ...s.slice(3)] as Signup));

    function format_signups(signup: Signup): string[] {
        return [
            signup[0].toString(),
            people_names.get(signup[1]),
            signup[2].toLocaleString(),
            signup[3] ? "Yes" : "No",
            signup[4] ? "Yes" : "No",
            (signup[5] & FRIDAY) != 0 ? "✅" : "",
            (signup[5] & SATURDAY) != 0 ? "✅" : "",
            (signup[5] & SUNDAY) != 0 ? "✅" : "",
            signup[6] ? "Yes" : "No",
            signup[7]
        ];
    }

</script>

<table>

    <thead>
        <tr>
            <th>ID</th>
            <th>Person</th>
            <th>Completed</th>
            <th>Trial?</th>
            <th>Attending briefing?</th>
            <th>Fri</th>
            <th>Sat</th>
            <th>Sun</th>
            <th>Has car?</th>
            <th>Notes</th>
        </tr>
    </thead>

    <tbody>
        {#each signups as signup, row_index}
            <tr class="{row_index % 2 == 0 ? 'even-row' : 'odd-row'}">
                {#each format_signups(signup) as col}
                    <td>{col}</td>
                {/each}
            </tr>
        {/each}
    </tbody>

</table>
