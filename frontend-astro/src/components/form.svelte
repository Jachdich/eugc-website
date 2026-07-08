
<script lang="ts">
    // TODOOOOOOOO TODO TODO make this work without JS
    import YesNo from "./YesNo.svelte";
    const FRIDAY   = 0b0010000;
    const SATURDAY = 0b0100000;
    const SUNDAY   = 0b1000000;

    let name: string = $state("");
    let phone: string = $state("");
    let email: string = $state("");
    let notes: string = $state("");
    let trial: "yes" | "no" | undefined = $state();
    let briefing: "yes" | "no" | undefined = $state();
    let friday: boolean = $state(false);
    let saturday: boolean = $state(false);
    let sunday: boolean = $state(false);
    let car: "yes" | "no" | undefined = $state();

    let tried_submit = $state(false);

    function submit() {
        tried_submit = true;
        if (
            name.trim() !== "" &&
            phone.trim() !== "" &&
            email.trim() !== "" &&
            trial !== undefined &&
            (trial === "no" || briefing !== undefined)
        ) {
            let availability = 0;
            if (friday) availability |= FRIDAY;
            if (saturday) availability |= SATURDAY;
            if (sunday) availability |= SUNDAY;
            const packet = {
                name: name,
                phone: phone,
                email: email,
                trial: trial == "yes",
                briefing: briefing == "yes",
                availability: availability,
                car: car == "yes",
                notes: notes,
            };
            fetch("/api/v1/availability_form", {
              method: "POST",
              body: JSON.stringify(packet),
              headers: {
                "Content-type": "application/json; charset=UTF-8"
              }
            });
        }
        return false;
    }
    
</script>

<h3>EUGC Flying Availability Form</h3>

<span class="required">*</span> required
<form onsubmit={submit}>

  <div class="question">
    <label for="name">1. Please enter your full name <span class="required">*</span></label>
    <input id="name" type="text" required bind:value={name} class={name.trim() === "" && tried_submit ? 'highlight-required' : ''}/>
  </div>

  <div class="question">
    <p>2. Is this your trial flight? <span class="required">*</span></p>
    <YesNo name="trial" bind:value={trial} highlight_required={trial === undefined && tried_submit} />
  </div>

{#if trial == "yes"}
  <div class="question">
    <p>2.5. Do you plan to attend the briefing? <span class="required">*</span></p>
    <YesNo name="brief" bind:value={briefing} highlight_required={trial === "yes" && briefing === undefined && tried_submit} />
  </div>
{/if}

  <div class="question">
    <p>3. Which days are you available?</p>
    <!-- <p>N.B. This <strong>only indicates your availability</strong>. We <strong>cannot guarantee</strong> that you are selected for any given day.</p>-->
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
    <input id="notes" bind:value={notes} type="text" />
  </div>

  <div class="question">
    <label for="email">5. Email Address <span class="required">*</span></label>
    <input id="email" type="email" bind:value={email} required class={email.trim() === "" && tried_submit ? 'highlight-required' : ''}/>
  </div>

  <div class="question">
    <label for="phone">6. Phone Number (incase we need to call you) <span class="required">*</span></label>
    <input id="phone" type="text" bind:value={phone} required class={phone.trim() === "" && tried_submit ? 'highlight-required' : ''} />
  </div>
 

  <div class="question">
    <p>7. Do you have a car (and would be willing to help with transport)? <span class="required">*</span></p>
    <YesNo name="car" bind:value={car} highlight_required={false}/>
  </div>

  <input type="submit" />

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

.highlight-required {
    border: 2px solid red;
    border-radius: 5px;
}


</style>
