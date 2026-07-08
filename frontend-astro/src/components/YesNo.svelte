
<script lang="ts">
    interface Props {
        value: "yes" | "no" | undefined,
        name: string,
        highlight_required: boolean,
    }

    let { value = $bindable(), name, highlight_required }: Props = $props();


</script>

<div class="radio-group {highlight_required ? 'highlight-required' : ''}">
    <div class="radio">
      <input type="radio" id="yes-{name}" name={name} value="yes" bind:group={value} />
      <label for="yes-{name}">Yes</label>
    </div>
    <div class="radio">
      <input type="radio" id="no-{name}" name={name} value="no" bind:group={value} />
      <label for="no-{name}">No</label>
    </div>
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
