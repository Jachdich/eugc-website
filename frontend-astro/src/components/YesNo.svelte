
<script lang="ts">
    import Radio from "./Radio.svelte";
    interface Props {
        value: "Yes" | "No" | undefined,
        name: string,
        highlight_required: boolean,
    }

    let { value = $bindable(), name, highlight_required }: Props = $props();

    let raw_value: string | undefined = $state(undefined);
</script>

<Radio bind:value={value} choices={["Yes", "No"]} {highlight_required} {name} /> 
