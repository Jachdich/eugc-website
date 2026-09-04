<!--
<script lang="ts">
    interface Props {
        person: number,
        people: any[][],
    }

    let { people, person = $bindable() }: Props = $props();
    let person_looked_up = $derived(lookup_name(person));
    let person_value: string = $derived(person_looked_up === undefined ? "" : person_looked_up);

    function lookup_name(id: number): string | undefined {
        for (const p of people) {
            if (p[0] == id) {
                return p[1];
            }
        }
        return undefined;
    }

    let opened = $state(false);

    function input(e: any) {
        
    }

    function focus() {
        opened = true;
    }
    function blur() {
        opened = false;
    }

    function filtered(people: any[][]): any[][] {
        return people.filter((p) => p[1].toLowerCase().includes(person_value.toLowerCase()));
    }

    function select_person(person_sel: number) {
        person = person_sel;
        console.log(person);
    }

</script>
<input type="text" bind:value={person_value} oninput={input} onfocus={focus} onblur={blur} />
{#if opened}
<div style="height: 0px;">
<div role="menu" class="dropdown">
    {#each filtered(people) as person}
        <button onclick={() => select_person(person[0])}>{person[1]}</button>
    {/each}

</div>
</div>
{/if}

<style>

    input {
        border: none;
        min-width: 90px;
        field-sizing: content;
        flex-grow: 1;
        width: 0;
    }

    .dropdown {
        position: relative;
        max-height: 150px;
        overflow: scroll;
        background-color: white;
        display: flex;
        flex-direction: column;
    }
</style>

-->
<script lang="ts">
    interface Props {
        person: number,
        people: Map<number, string>,
        onchange: ((_: number) => void) | undefined,
    }

    let { people, person = $bindable(), onchange }: Props = $props();

</script>

<select bind:value={person} onchange={() => onchange !== undefined ? onchange(Number.parseInt(person.toString())) : undefined}>
    <option value="-1"></option>
    {#each people.entries() as person_s}
        <option value="{person_s[0]}" selected={person_s[0] == person}>{person_s[1]}</option>
    {/each}
</select>

<style>
    select {
        min-width: 140px;
        field-sizing: content;
        flex-grow: 1;
        width: 0;
    }

</style>
