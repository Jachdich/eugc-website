<script lang="ts">
    interface Props {
        value: string | undefined,
        name: string,
        choices: string[],
        highlight_required: boolean,
    }

    let { value = $bindable(), name, highlight_required, choices }: Props = $props();


</script>

<div class="radio-group {highlight_required ? 'highlight-required' : ''}">
    {#each choices as choice}
        <div class="radio">
          <input type="radio" id="{choice}-{name}" name={name} value="{choice}" bind:group={value} />
          <label for="{choice}-{name}" class="radio-label">{choice}</label>
        </div>
    {/each}
</div>

<style>
.radio {
    display: flex;
    flex-direction: row;
}
.highlight-required {
    border: 2px solid red;
    border-radius: 5px;
}
</style>
