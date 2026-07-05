
<script lang="ts">
    import YesNo from "./YesNo.svelte";

    let trial: "yes" | "no" | undefined;
    let briefing: "yes" | "no" | undefined;
    let friday: boolean = false;
    let saturday: boolean = false;
    let sunday: boolean = false;
    let car: "yes" | "no" | undefined;

</script>


<span class="required">*</span> required
<form>

  <div class="question">
    <label for="name">1. Please enter your full name <span class="required">*</span></label>
    <input id="name" type="text" required/>
  </div>

  <div class="question">
    <p>2. Is this your trial flight? <span class="required">*</span></p>
    <YesNo name="trial" bind:value={trial} />
  </div>

{#if trial == "yes"}
  <div class="question">
    <p>2.5. Do you plan to attend the briefing? <span class="required">*</span></p>
    <YesNo name="brief" bind:value={briefing} />
  </div>
{/if}

  <div class="question">
    <p>3. Which days are you available?</p>
    <div class="inline">
        <input type="checkbox" id="friday" bind:checked={friday} />
        <label for="friday">Friday</label>
    </div>
    <div class="inline">
        <input type="checkbox" id="saturday" bind:checked={saturday} />
        <label for="saturday">Saturday</label>
    </div>
    <div class="inline">
        <input type="checkbox" id="sunday" bind:checked={sunday} />
        <label for="sunday">Sunday</label>
    </div>
  </div>

  <div class="question">
    <label for="notes">4. Notes/comments (optional)</label>
    <input id="notes" type="text" />
  </div>

  <div class="question">
    <label for="email">5. Email Address <span class="required">*</span></label>
    <input id="email" type="email" required />
  </div>

  <div class="question">
    <label for="phone">6. Phone Number (incase we need to call you) <span class="required">*</span></label>
    <input id="phone" type="text" required />
  </div>
 

  <div class="question">
    <p>7. Do you have a car (and would be willing to help with transport)? <span class="required">*</span></p>
    <YesNo name="car" bind:value={car} />
  </div>
  

</form>
<style>

.question {
    display: flex;
    flex-direction: column;
    width: fit-content;
}

label, p {
    margin: 16px 0px;
}

input[type="text"], input[type="email"] {
    width: 200px;
}

.required {
    color: red;
}


</style>
