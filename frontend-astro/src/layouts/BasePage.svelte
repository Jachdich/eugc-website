

<script>
    import { onMount } from "svelte";

    let db = false;
	onMount(() => {
		db = window.location.href.split("/").includes("db");
		console.log(window.navigator.href);
	});
</script>

    <div id="whole-page">
      <div id="nav">
      	{#if db}
      		<p>DB BIT</p>
      	{:else}
      		<p>Not DB bit</p>
      	{/if}
      </div>
      <div id="main-content">
      </div>
    </div>

<style>
	html,
	body {
		margin: 0;
		width: 100%;
		height: 100%;
    font-family: sans-serif;
	}

  #main-content {
    max-width: 1024px;
  }

  #whole-page {
    display: flex;
    flex-direction: row;
  }
</style>
