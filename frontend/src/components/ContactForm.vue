<template>
  <div class="modal-backdrop" @click.self="close">

    <div class="contact-form">

      <div class="form-header">
        <div>
          <p class="eyebrow">NEW CONTACT</p>
          <h2>Add Contact</h2>
        </div>

        <button
          class="close-button"
          @click="close"
          aria-label="Close"
        >
          ×
        </button>
      </div>


      <form @submit.prevent="submitForm">

        <!-- NAME -->

        <div class="form-field">
          <label for="name">
            Name <span>*</span>
          </label>

          <input
            id="name"
            v-model="form.name"
            type="text"
            placeholder="e.g. Rahul Sharma"
            :class="{ invalid: errors.name }"
          />

          <small v-if="errors.name">
            {{ errors.name }}
          </small>
        </div>


        <!-- PHONE -->

        <div class="form-field">
          <label for="phone">
            Phone number <span>*</span>
          </label>

          <input
            id="phone"
            v-model="form.phone_number"
            type="tel"
            placeholder="+91 98765 43210"
            :class="{ invalid: errors.phone_number }"
          />

          <small v-if="errors.phone_number">
            {{ errors.phone_number }}
          </small>
        </div>


        <!-- EMAIL -->

        <div class="form-field">
          <label for="email">
            Email
          </label>

          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="rahul@example.com"
            :class="{ invalid: errors.email }"
          />

          <small v-if="errors.email">
            {{ errors.email }}
          </small>
        </div>


        <!-- ADDRESS -->

        <div class="form-field">
          <label for="address">
            Address
          </label>

          <textarea
            id="address"
            v-model="form.address"
            placeholder="Mumbai, Maharashtra"
            rows="3"
          ></textarea>
        </div>

        <div class="form-field">
          <label for="tags">Labels</label>
          <LabelSelector v-model="form.tags" />
        </div>


        <!-- BACKEND ERROR -->

        <div v-if="serverError" class="server-error">
          {{ serverError }}
        </div>


        <!-- ACTIONS -->

        <div class="form-actions">

          <button
            type="button"
            class="cancel-button"
            @click="close"
            :disabled="saving"
          >
            Cancel
          </button>

          <button
            type="submit"
            class="save-button"
            :disabled="saving"
          >

            <span v-if="saving" class="button-spinner"></span>

            {{ saving ? "Saving..." : "Save Contact" }}

          </button>

        </div>

      </form>

    </div>

  </div>
</template>


<script setup>
import { reactive, ref } from "vue";
import { useContactsStore } from "../stores/contacts";
import LabelSelector from "./LabelSelector.vue";

const emit = defineEmits(["close", "created"]);

const store = useContactsStore();

const saving = ref(false);
const serverError = ref("");

const form = reactive({
  name: "",
  phone_number: "",
  email: "",
  address: "",
  tags: [],
});

const errors = reactive({
  name: "",
  phone_number: "",
  email: "",
});


function validate() {

  errors.name = "";
  errors.phone_number = "";
  errors.email = "";

  let valid = true;


  if (!form.name.trim()) {
    errors.name = "Name is required.";
    valid = false;
  }


  if (!form.phone_number.trim()) {
    errors.phone_number = "Phone number is required.";
    valid = false;
  } else if (!/^\+?[0-9\s-]{7,20}$/.test(form.phone_number)) {
    errors.phone_number = "Enter a valid phone number.";
    valid = false;
  }


  if (
    form.email &&
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)
  ) {
    errors.email = "Enter a valid email address.";
    valid = false;
  }


  return valid;
}


async function submitForm() {

  serverError.value = "";

  if (!validate()) {
    return;
  }

  saving.value = true;

  try {

    await store.createContact({
      name: form.name.trim(),
      phone_number: form.phone_number.trim(),
      email: form.email.trim() || null,
      address: form.address.trim() || null,
      tags: form.tags,
    });

    emit("created");

    close();

  } catch (error) {

    if (error.response?.data?.detail) {
      serverError.value = error.response.data.detail;
    } else {
      serverError.value =
        "Unable to save contact. Please try again.";
    }

  } finally {
    saving.value = false;
  }
}


function close() {
  if (!saving.value) {
    emit("close");
  }
}
</script>