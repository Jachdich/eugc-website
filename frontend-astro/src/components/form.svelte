
<script lang="ts">
    import YesNo from "./YesNo.svelte";
    import "./form.css";
    const FRIDAY   = 0b0010000;
    const SATURDAY = 0b0100000;
    const SUNDAY   = 0b1000000;

    let notes: string = $state("");
    let trial: "Yes" | "No" | undefined = $state();
    let briefing: "Yes" | "No" | undefined = $state();
    let friday: boolean = $state(false);
    let saturday: boolean = $state(false);
    let sunday: boolean = $state(false);
    let car: "Yes" | "No" | undefined = $state();

    let tried_submit = $state(false);

    function submit(e: Event) {
        e.preventDefault();
        tried_submit = true;
        if (
            trial !== undefined &&
            (trial === "No" || briefing !== undefined)
        ) {
            let availability = 0;
            if (friday) availability |= FRIDAY;
            if (saturday) availability |= SATURDAY;
            if (sunday) availability |= SUNDAY;

            const packet = {
                trial: trial == "Yes",
                briefing: briefing == "Yes",
                availability: availability,
                car: car == "Yes",
                notes: notes,
            };
            fetch("/api/v1/availability_form", {
              method: "POST",
              body: JSON.stringify(packet),
              headers: {
                "Content-type": "application/json; charset=UTF-8"
              }
            }).then((response) => {
                if (response.status == 200) {
                    window.location.href = "/form-success";
                } else {
                    alert("Server sent error code: " + response.status);
                    window.location.href = "/form-failure";
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
    <p>1. Is this your trial flight? <span class="required">*</span></p>
    <YesNo name="trial" bind:value={trial} highlight_required={trial === undefined && tried_submit} />
  </div>

{#if trial == "Yes"}
  <div class="question">
    <p>1.5. Do you plan to attend the briefing? <span class="required">*</span></p>
    <YesNo name="brief" bind:value={briefing} highlight_required={trial === "Yes" && briefing === undefined && tried_submit} />
  </div>
{/if}

  <div class="question">
    <p>2. Which days are you available?</p>
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
    <label for="notes">3. Notes/comments (optional)</label>
    <input id="notes" bind:value={notes} type="text" />
  </div>

  <div class="question">
    <p>4. Do you have a car (and would be willing to help with transport)? <span class="required">*</span></p>
    <YesNo name="car" bind:value={car} highlight_required={false}/>
  </div>

  <input type="submit" value="Submit" />

</form>
