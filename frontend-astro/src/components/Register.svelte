<script lang="ts">
    import "./form.css";
    import Radio from "./Radio.svelte";
    let name: string = $state("");
    let phone: string = $state("");
    let email: string = $state("");
    let pass: string = $state("");
    let tourist: string | undefined = $state();

    let tried_submit = $state(false);

    function submit(e: Event) {
        e.preventDefault();
        tried_submit = true;
        if (
            name.trim() !== "" &&
            phone.trim() !== "" &&
            email.trim() !== "" &&
            pass != "") {
            let tourist_idx = 0;
            if (tourist === "Experience gliding") {
                tourist_idx = 2;
            } else if (tourist === "Not sure yet") {
                tourist_idx = 1;
            } else if (tourist === "Learn to fly") {
                tourist_idx = 0;
            }

            const packet = {
                name: name.trim(),
                phone: phone.trim(),
                email: email.trim(),
                password: pass,
                tourist: tourist_idx,
            };
            
            fetch("/eugc/api/v1/register", {
              method: "POST",
              body: JSON.stringify(packet),
              headers: {
                "Content-type": "application/json; charset=UTF-8"
              }
            }).then((response) => {
                if (response.status == 200) {
                    window.location.href = "/eugc/form-success";
                } else if (response.status == 409) {
                    alert("Unable to create account, email already exists in the system");
                    window.location.href = "/eugc/form-failure";
                } else {
                    alert("Server sent error code: " + response.status);
                    window.location.href = "/eugc/form-failure";
                }
            });
        }
    }
</script>


<h3>EUGC Flying Account Registration</h3>

<p class="required-container"><span class="required">*</span> required</p>
<form onsubmit={submit}>
  <div class="question">
    <label for="name">1. Please enter your full name <span class="required">*</span></label>
    <input id="name" type="text" required bind:value={name} class={name.trim() === "" && tried_submit ? 'highlight-required' : ''}/>
  </div>
  <div class="question">
    <label for="email">2. Email Address <span class="required">*</span></label>
    <input id="email" type="email" bind:value={email} required class={email.trim() === "" && tried_submit ? 'highlight-required' : ''}/>
  </div>

  <div class="question">
      <label for="pass">3. Create a password <span class="required">*</span></label>
      <input id="pass" type="password" bind:value={pass} required class={pass === "" && tried_submit ? "highlight-required" : ""}/>
  </div>

  <div class="question">
    <label for="phone">4. Phone Number (incase we need to call you) <span class="required">*</span></label>
    <input id="phone" type="text" bind:value={phone} required class={phone.trim() === "" && tried_submit ? 'highlight-required' : ''} />
  </div>
  <div class="question">
    <p>5. What do want to get out of flying with us? <span class="required">*</span></p>
    <Radio name="tourist" choices={["Experience gliding", "Learn to fly", "Not sure yet"]} bind:value={tourist} highlight_required={tourist === undefined && tried_submit} />
  </div>

  <input type="submit" />
</form>
