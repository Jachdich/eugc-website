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

<div class="pan-navbar">
  <span class="lab-nav-title">
    Edinburgh University <br>
    <span style="font-size: 31px;">
      Gliding Club
    </span>
  </span>

  <a class="link-nav-element" href="/">Home</a>
  <a class="link-nav-element" href="/gettingstarted">Getting Started</a>
  <a class="link-nav-element" href="/intro">What is Gliding?</a>
  <a class="link-nav-element" href="/trial">Trial Lessons</a>
  <a class="link-nav-element" href="/training">Training</a>
  <a class="link-nav-element" href="/comps">Comps & Trips</a>
  <a class="link-nav-element" href="/faq">FAQs</a>
  <a class="link-nav-element" href="/contact">Contact</a>

  {#if logged_in}
    <span class="lab-nav-element">Database</span>
    <a class="link-nav-element" href="/db/members">Member list</a>
    <a class="link-nav-element" href="/db/signups">Signups</a>
    <a class="link-nav-element" href="/db/briefings">Briefings</a>
    <a class="link-nav-element" href="/db/org">Flying Organisation</a>
  {/if}

  <span class="lab-nav-element">
    {#if uname !== undefined}
      {uname}
    {:else}
      Account
    {/if}
  </span>

  {#if logged_in}
    <a class="link-nav-element" href="/api/v1/logout">Log out</a>
  {:else}
    <a class="link-nav-element" href="/login">Log in</a>
  {/if}
</div>

<style>
  @media (orientation: landscape) {
    .pan-navbar {
      height: calc(100% - 32px);

      background-color: var(--col-panel-1);

      display: flex;
      flex-direction: column;
      gap: 8px;
      
      padding-top: 32px;
      padding-left: 96px;

      font-size: 18px;
    }

    .link-nav-element {
      text-decoration: none;

      color: var(--text-white);

      background-color: var(--col-panel-2);

      padding: 8px;
      padding-left: 14px;
      border-top-left-radius: 16px;
      border-bottom-left-radius: 16px;
    }
    .link-nav-element:hover {
      background-color: var(--col-accent);
    }

    .lab-nav-element {
      margin-top: 16px;
      margin-bottom: 8px;

      text-align: center;
    }
  }

  @media (orientation: portrait) {
    .pan-navbar {
      height: calc(100% - 32px);

      background-color: var(--col-panel-1);

      display: flex;
      flex-direction: column;
      gap: 8px;
      
      /* padding-top: 32px;
      padding-left: 96px; */

      font-size: 18px;

      padding-bottom: 16px;
    }

    .link-nav-element {
      text-decoration: none;

      color: var(--text-white);

      background-color: var(--col-panel-2);

      padding: 8px;
      padding-left: 14px;
    }
    .lab-nav-element {
      margin-top: 16px;
      margin-bottom: 8px;

      text-align: center;
    }
  }

  .lab-nav-title {
    margin-top: 16px;
    margin-bottom: 24px;

    padding-left: 8px;

    font-family: "Lexend", sans-serif;
    font-size: 18px;
    font-weight: bold;

    text-align: left;
  }
</style>
