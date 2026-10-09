"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");

class Element {
  constructor(tag = "div") {
    this.tagName = tag;
    this.children = [];
    this.listeners = {};
    this.disabled = false;
    this.value = "";
    this.textContent = "";
    this.className = "";
  }
  attachShadow() { this.shadowRoot = new Element("shadow"); return this.shadowRoot; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = [...children]; }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  setAttribute(key, value) { this[key] = value; }
  click() { if (!this.disabled) this.listeners.click?.(); }
}
function elements(node, predicate, out = []) {
  if (predicate(node)) out.push(node);
  for (const child of node.children || []) elements(child, predicate, out);
  return out;
}
function createCard(file, name) {
  const registrations = new Map();
  const context = vm.createContext({
    HTMLElement: Element,
    document: { createElement: (tag) => new Element(tag) },
    customElements: {
      get: key => registrations.get(key),
      define: (key, value) => registrations.set(key, value),
    },
  });
  vm.runInContext(fs.readFileSync(file, "utf8"), context, { filename: file });
  return new (registrations.get(name))();
}
const path = "dashboard/heating-scheduler-workflow-preview.js";

test("mobile preview loads only read-only schedule service", async () => {
  const card = createCard(path, "heating-scheduler-workflow-preview");
  const requests = [];
  card.hass = { callWS: async request => {
    requests.push(request);
    return { response: { read_only: true, items: [
      { title: "Morning", subtitle: "07:00 · 30 min", status: "Disabled",
        can_delete_after_confirmation: true, start: "07:00",
        minutes: 30, weekdays: ["mon", "tue"], enabled: false },
      { title: "Afternoon", status: "Enabled", can_delete_after_confirmation: false }
    ] } };
  } };
  card.setConfig({ entry_id: "disposable_entry" });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(requests.length, 1);
  assert.equal(requests[0].service, "list_schedules");
  assert.equal(requests[0].return_response, true);
  assert.equal(card._rows.length, 2);
  const buttons = () => elements(card.shadowRoot, node => node.tagName === "button");
  buttons().find(b => b.textContent === "Manage Schedules").click();
  assert.equal(card._view, "manage");
  assert.equal(buttons().filter(b => b.textContent === "🗑 Review").length, 1);
  buttons().find(b => b.textContent === "🗑 Review").click();
  assert.equal(card._view, "delete_preview");
  assert.equal(buttons().find(b => b.textContent === "Confirm deletion — unavailable").disabled, true);
  buttons().find(b => b.textContent === "Cancel").click();
  assert.equal(card._view, "manage");
  assert.equal(requests.length, 1);
});

test("add form offers seven disabled weekday inputs and disabled save", () => {
  const card = createCard(path, "heating-scheduler-workflow-preview");
  card.setConfig({ entry_id: "disposable_entry" });
  const buttons = () => elements(card.shadowRoot, node => node.tagName === "button");
  buttons().find(b => b.textContent === "Add Schedule (preview)").click();
  const weekday = elements(card.shadowRoot, node => node.tagName === "fieldset")[0];
  assert.equal(weekday.disabled, true);
  assert.equal(elements(weekday, node => node.type === "checkbox").length, 7);
  assert.equal(elements(card.shadowRoot, node => node.tagName === "input").every(n => n.disabled), true);
  assert.equal(buttons().find(b => b.textContent === "Save — unavailable").disabled, true);
});
