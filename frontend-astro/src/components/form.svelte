
<script lang="ts">
    import YesNo from "./YesNo.svelte";
    import "./form.css";
    import { onMount } from "svelte";
    let logged_in = $state(false);
    async function check_logged_in() {
        let response = await fetch("/eugc/api/v1/is_logged_in");
        let json = await response.json();
        logged_in = json["logged_in"];
    }
	onMount(() => {
      check_logged_in();
	});

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
    let bike: "Yes" | "No" | undefined = $state();

    let tried_submit = $state(false);

    function mod(n: number, m: number) {
        return ((n % m) + m) % m;
    }

    function add_days(date: Date, days: number): Date {
        let new_date = new Date(date.valueOf());
        new_date.setDate(new_date.getDate() + days);
        return new_date;
    }
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    function format_day(date: Date): string {
        const date_str = date.getDate().toString();
        const last_digit = date_str.slice(-1);
        const second_last = date_str.slice(-2).slice(0, 1);
        let suffix = "th";
        if (second_last != "1") {
            if (last_digit == "1") {
                suffix = "st";
            } else if (last_digit == "2") {
                suffix = "nd";
            } else if (last_digit == "3") {
                suffix = "rd";
            }
        }
        return `the ${date.getDate()}${suffix} of ${months[date.getMonth()]}`;
    }
    let now = new Date();
    let day_of_week = mod(now.getDay() - 1, 6);
    let days_till_friday = mod(4 - day_of_week, 6);
    let fri_date = format_day(add_days(now, days_till_friday));
    let sat_date = format_day(add_days(now, days_till_friday + 1));
    let sun_date = format_day(add_days(now, days_till_friday + 2));

    let in_date = !(day_of_week == 4 || day_of_week == 5 || day_of_week == 6);

    function submit(e: Event) {
        e.preventDefault();
        tried_submit = true;
        if (
            trial !== undefined &&
            (trial === "No" || briefing !== undefined) &&
            (friday || saturday || sunday)
        ) {
            let availability = 0;
            if (friday) availability |= FRIDAY;
            if (saturday) availability |= SATURDAY;
            if (sunday) availability |= SUNDAY;

            const packet = {
                trial: trial === "Yes",
                briefing: briefing === "Yes",
                availability: availability,
                car: car === "Yes",
                bike: bike === "Yes",
                notes: notes,
            };
            fetch("/eugc/api/v1/availability_form", {
              method: "POST",
              body: JSON.stringify(packet),
              headers: {
                "Content-type": "application/json; charset=UTF-8"
              }
            }).then((response) => {
                if (response.status == 200) {
                    window.location.href = "/eugc/form-success";
                } else {
                    alert("Server sent error code: " + response.status);
                    window.location.href = "/eugc/form-failure";
                }
            });
        }

        return false;
    }
    
</script>

<h3>EUGC Flying Availability Form</h3>


{#if logged_in}
    <div class="required-container">
        <h3>Important Information</h3>
        <p>Signups are done on a <strong>weekly basis</strong>. This form indicates your availability for the next coming weekend.</p>
        <p>Please only sign up when you know you are free for the selected days. This is <strong>not</strong> a first-come, first-served system. You will be considered equally no matter when you fill in the form (before Thursday, when we usually send out confirmations), so don't feel like you have to sign up before you know your availability.</p>
        <p>This form <strong>only indicates your availability</strong>. You will be contacted by email and/or whatsapp with further instructions if you are selected to fly. Please <strong>do not</strong> show up to the airfield by yourself unless agreed with the Committee.</p>
        <p>If you find your availability has changed, just submit this form again which will overwrite your previous submission.</p>
        {#if in_date}
            <p><span class="required">*</span> required</p>
            <form onsubmit={submit}>

              <div class="question">
                <p>1. Is this your trial flight? <span class="required">*</span></p>
                <YesNo name="trial" bind:value={trial} highlight_required={trial === undefined && tried_submit} />
              </div>

            {#if trial == "Yes"}
              <div class="question">
                <p>1.5. Do you plan to attend the briefing? <span class="required">*</span></p>
                <p style="margin-top: -12px; margin-bottom: 16px;">N.B. You are only required to attend one briefing, unless it has been a long time (let's say, 1 semester) since you attended one, or last flew.</p>
                <YesNo name="brief" bind:value={briefing} highlight_required={trial === "Yes" && briefing === undefined && tried_submit} />
              </div>
            {/if}

              <div class={(!friday) && (!saturday) && (!sunday) && tried_submit ? "question highlight-required" : "question"}>
                <p>2. Which days are you available? <span class="required">*</span></p>
                <p style="margin-top: -12px; margin-bottom: 16px;">N.B. This <strong>only indicates your availability</strong>. We <strong>cannot guarantee</strong> that you are selected for any given day.</p>
                <div class="inline">
                    <input type="checkbox" id="friday" bind:checked={friday} />
                    <label for="friday">Friday {fri_date}</label>
                </div>
                <div class="inline">
                    <input type="checkbox" id="saturday" bind:checked={saturday} />
                    <label for="saturday">Saturday {sat_date}</label>
                </div>
                <div class="inline">
                    <input type="checkbox" id="sunday" bind:checked={sunday} />
                    <label for="sunday">Sunday {sun_date}</label>
                </div>
              </div>

              <div class="question">
                <label for="notes">3. Notes/comments (optional)</label>
                <input id="notes" bind:value={notes} type="text" />
              </div>

              <div class="question">
                <p>4. Do you have a car (and would be willing to help with transport)? <span class="required">*</span></p>
                <YesNo name="car" bind:value={car} highlight_required={car === undefined && tried_submit}/>
              </div>
              <div class="question">
                <p>5. Do you have a bike (and would be willing to cycle 30 minutes)? <span class="required">*</span></p>
                <YesNo name="bike" bind:value={bike} highlight_required={bike === undefined && tried_submit}/>
              </div>

              <input type="submit" value="Submit" />

            </form>
        {:else}
            <h2>Hold on!</h2>
            <p>
                It's already past Thursday, which means flying has <i>probably</i> been organised for this weekend already.
                For the sake of reducing confusion, the flying form is closed over the period while flying is happening
                 (otherwise you might find yourself signing up for yesterday, which makes no sense). Come back on
                Monday to select your availability for the coming weekend.
            </p>

            <p>
                If you have any last-minute changes to your availability it's best to get in contact directly (email, or whatsapp)
                as we won't be checking this form after we've already decided who's flying.
            </p>
        {/if}
    </div>
{:else}
    <p>You must be logged in to submit your availability. Please either <a href="/eugc/login">log in</a> or <a href="/eugc/register">register</a> for an account with us.</p>
{/if}
