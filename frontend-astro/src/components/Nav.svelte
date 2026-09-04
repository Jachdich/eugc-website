

<script lang="ts">
    import { onMount } from "svelte";
    let logged_in = false;
    let uname: string | undefined = undefined;
    async function check_logged_in() {
        let response = await fetch("/api/v1/is_logged_in");
        let json = await response.json();
        logged_in = json["logged_in"];
        uname = json["uname"];
    }
	onMount(() => {
      check_logged_in();
	});
</script>

<div id="sidebar">
  <ul>
    <li><a href="/">Home</a></li>
    <li><a href="/gettingstarted">Getting Started</a></li>
    <li><a href="/">What is Gliding?</a></li>
    <li><a href="/">Trial Lessons</a></li>
    <li><a href="/">Training</a></li>
    <li><a href="/">Comps & Trips</a></li>
    <li><a href="/">FAQs</a></li>
    <li><a href="/contact">Contact</a></li>
    {#if logged_in}
      <li style="list-style-type: none; padding: 10px 0px">Database</li>
      <li><a href="/db/members">Member list</a></li>
      <li><a href="/db/signups">Signups</a></li>
      <li><a href="/db/briefings">Briefings</a></li>
      <li><a href="/db/org">Flying Organisation</a></li>
    {/if}
    <li style="list-style-type: none; padding: 10px 0px">Account {#if uname !== undefined}{uname}{/if}</li>
    {#if logged_in}
      <li><a href="/api/v1/logout">Log out</a></li>
    {:else}
      <li><a href="/login">Log in</a></li>
    {/if}
  </ul>
</div>

<style>
  #sidebar {
    width: 200px;
  }
</style>
