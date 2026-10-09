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

test("failed or malformed read-only response reports error without mutations", async () => {
  const card = createCard(path, "heating-scheduler-workflow-preview");
  const requests = [];
  card.hass = { callWS: async request => {
    requests.push(request);
    return { response: { read_only: false, items: [] } };
  } };
  card.setConfig({ entry_id: "disposable_a" });
  await new Promise(resolve => setImmediate(resolve));
  assert.match(card._error, /Read-only schedule response unavailable/);
  assert.equal(card._rows.length, 0);
  assert.equal(requests.length, 1);
  assert.equal(requests[0].service, "list_schedules");
});

test("changing config invalidates outdated responses", async () => {
  const card = createCard(path, "heating-scheduler-workflow-preview");
  let releaseOld;
  const requests = [];
  card.hass = { callWS: request => {
    requests.push(request);
    if (request.service_data.entry_id === "disposable_old")
      return new Promise(resolve => { releaseOld = resolve; });
    return Promise.resolve({response:{read_only:true,items:[{title:"New"}]}});
  } };
  card.setConfig({entry_id:"disposable_old"});
  card.setConfig({entry_id:"disposable_new"});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(requests.length, 2);
  assert.equal(card._rows[0].title, "New");
  releaseOld({response:{read_only:true,items:[{title:"Old"}]}});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(card._rows[0].title, "New");
});

test("empty owned schedule list renders safely", async () => {
  const card = createCard(path, "heating-scheduler-workflow-preview");
  card.hass = {callWS:async () => ({response:{read_only:true,items:[]}})};
  card.setConfig({entry_id:"disposable_empty"});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(card._rows.length, 0);
  assert.equal(card._error, "");
  assert.equal(card._view, "control");
});

test("edit preview never enables controls even for valid schedule", async () => {
  const card = createCard(path, "heating-scheduler-workflow-preview");
  card.hass = {callWS:async () => ({response:{read_only:true,items:[
    {title:"Morning",status:"Enabled",enabled:true,minutes:60,
     weekdays:["mon","fri"],start:"07:30",can_delete_after_confirmation:false}
  ]}})};
  card.setConfig({entry_id:"disposable_edit"});
  await new Promise(resolve => setImmediate(resolve));
  const buttons = () => elements(card.shadowRoot, node => node.tagName === "button");
  buttons().find(b => b.textContent === "Morning").click();
  assert.equal(card._view,"edit");
  const time = elements(card.shadowRoot, node => node.type === "time")[0];
  assert.equal(time.value,"07:30");
  assert.equal(time.disabled,true);
  const select = elements(card.shadowRoot, node => node.tagName === "select")[0];
  assert.equal(select.value,"60");
  assert.equal(select.disabled,true);
  assert.equal(buttons().find(b => b.textContent === "Save — unavailable").disabled,true);
});

test("refresh updates selected schedule and closes invalid delete review", async () => {
  const card = createCard(path, "heating-scheduler-workflow-preview");
  let state = "Disabled";
  card.hass = { callWS: async () => ({response:{read_only:true,items:[
    {entity_id:"switch.schedule_a",title:"Morning",status:state,
      can_delete_after_confirmation:state==="Disabled",enabled:state==="Enabled"}
  ]}})};
  card.setConfig({entry_id:"disposable_refresh"});
  await new Promise(resolve=>setImmediate(resolve));
  const buttons=()=>elements(card.shadowRoot,n=>n.tagName==="button");
  buttons().find(b=>b.textContent==="Manage Schedules").click();
  buttons().find(b=>b.textContent==="🗑 Review").click();
  assert.equal(card._view,"delete_preview");
  state="Enabled";
  buttons().find(b=>b.textContent==="Refresh").click();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(card._view,"manage");
  assert.equal(card._selected.status,"Enabled");
  assert.equal(buttons().some(b=>b.textContent==="🗑 Review"),false);
});

test("refresh removes deleted selection from the preview", async () => {
  const card=createCard(path,"heating-scheduler-workflow-preview");
  let items=[{entity_id:"switch.schedule_a",title:"Morning",status:"Disabled"}];
  card.hass={callWS:async()=>({response:{read_only:true,items}})};
  card.setConfig({entry_id:"disposable_remove"});
  await new Promise(resolve=>setImmediate(resolve));
  let buttons=()=>elements(card.shadowRoot,n=>n.tagName==="button");
  buttons().find(b=>b.textContent==="Morning").click();
  assert.equal(card._view,"edit");
  items=[];
  buttons().find(b=>b.textContent==="Refresh").click();
  await new Promise(resolve=>setImmediate(resolve));
  assert.equal(card._view,"control");
  assert.equal(card._selected,null);
});

test("mobile layout uses wrap and touch-sized controls", () => {
  const source=fs.readFileSync(path,"utf8");
  assert.match(source, /@media \(max-width: 420px\)/);
  assert.match(source, /min-height:44px/);
  assert.match(source, /flex-wrap:wrap/);
});
