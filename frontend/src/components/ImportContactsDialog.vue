<template>
  <div class="modal-backdrop" @click.self="close">
    <div class="contact-form import-dialog" role="dialog" aria-modal="true" aria-labelledby="import-title">
      <div class="form-header">
        <div>
          <p class="eyebrow">CONTACTS</p>
          <h2 id="import-title">Import contacts</h2>
        </div>
        <button class="close-button" type="button" aria-label="Close import dialog" @click="close">×</button>
      </div>

      <p class="page-subtitle import-help">Choose a CSV containing name, phone_number, email, and address columns.</p>
      <label class="file-picker">
        <span>{{ fileName || "Choose CSV file" }}</span>
        <input type="file" accept=".csv,text/csv" @change="readFile" />
      </label>

      <div v-if="parseError" class="server-error">{{ parseError }}</div>
      <div v-if="rows.length" class="import-summary">
        <strong>{{ validRows.length }} ready to import</strong>
        <span>{{ errors.length }} row{{ errors.length === 1 ? "" : "s" }} need attention</span>
      </div>
      <ul v-if="errors.length" class="import-errors">
        <li v-for="error in errors.slice(0, 8)" :key="`${error.row}-${error.reason}`">Row {{ error.row }}: {{ error.reason }}</li>
        <li v-if="errors.length > 8">and {{ errors.length - 8 }} more...</li>
      </ul>

      <div class="form-actions">
        <button class="cancel-button" type="button" :disabled="saving" @click="close">Cancel</button>
        <button class="save-button" type="button" :disabled="!validRows.length || saving" @click="submit">
          {{ saving ? "Importing..." : `Import ${validRows.length || "contacts"}` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useContactsStore } from "../stores/contacts";

const emit = defineEmits(["close", "imported"]);
const store = useContactsStore();
const fileName = ref("");
const rows = ref([]);
const errors = ref([]);
const parseError = ref("");
const saving = ref(false);
const allowedHeaders = new Set(["name", "phone_number", "email", "address"]);
const phonePattern = /^\+?[0-9\s-]{7,20}$/;
const validRows = computed(() => rows.value);

function close() {
  if (!saving.value) emit("close");
}

function parseCsv(text) {
  const records = [];
  let record = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    const next = text[index + 1];
    if (character === '"' && quoted && next === '"') {
      field += '"';
      index += 1;
    } else if (character === '"') {
      quoted = !quoted;
    } else if (character === "," && !quoted) {
      record.push(field);
      field = "";
    } else if ((character === "\n" || character === "\r") && !quoted) {
      if (character === "\r" && next === "\n") index += 1;
      record.push(field);
      if (record.some((value) => value.trim())) records.push(record);
      record = [];
      field = "";
    } else {
      field += character;
    }
  }

  if (field || record.length) {
    record.push(field);
    if (record.some((value) => value.trim())) records.push(record);
  }
  return records;
}

function readFile(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  fileName.value = file.name;
  parseError.value = "";
  rows.value = [];
  errors.value = [];

  const reader = new FileReader();
  reader.onload = () => validateCsv(String(reader.result || ""));
  reader.onerror = () => { parseError.value = "Unable to read this file."; };
  reader.readAsText(file);
}

function validateCsv(text) {
  const records = parseCsv(text);
  if (records.length < 2) {
    parseError.value = "The CSV must contain a header row and at least one contact.";
    return;
  }

  const headers = records[0].map((header) => header.trim().toLowerCase());
  if (!headers.includes("name") || !headers.includes("phone_number")) {
    parseError.value = "CSV headers must include name and phone_number.";
    return;
  }

  const phoneNumbers = new Set();
  const emails = new Set();
  const valid = [];
  const invalid = [];

  records.slice(1).forEach((record, index) => {
    const rowNumber = index + 2;
    const values = Object.fromEntries(headers.map((header, valueIndex) => [header, record[valueIndex] || ""]));
    const name = values.name.trim();
    const phone_number = values.phone_number.trim();
    const email = values.email.trim() || null;
    const address = values.address.trim() || null;
    let reason = "";

    if (!name) reason = "Name is required";
    else if (!phone_number) reason = "Phone number is required";
    else if (!phonePattern.test(phone_number)) reason = "Invalid phone number";
    else if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) reason = "Invalid email";
    else if (phoneNumbers.has(phone_number)) reason = "Duplicate phone number in file";
    else if (email && emails.has(email.toLowerCase())) reason = "Duplicate email in file";

    if (reason) {
      invalid.push({ row: rowNumber, reason });
      return;
    }

    phoneNumbers.add(phone_number);
    if (email) emails.add(email.toLowerCase());
    valid.push({ name, phone_number, email, address, tags: [] });
  });

  rows.value = valid;
  errors.value = invalid;
}

async function submit() {
  saving.value = true;
  try {
    const result = await store.importContacts(validRows.value);
    emit("imported", result);
  } catch (error) {
    parseError.value = error.response?.data?.detail || "Unable to import contacts.";
  } finally {
    saving.value = false;
  }
}
</script>
