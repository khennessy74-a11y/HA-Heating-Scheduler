"use strict";
const { test } = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const { chromium } = require("@playwright/test");

const file = path.resolve("dashboard/heating-scheduler-workflow-preview.js");

async function makePage(browser, width = 375) {
  const page = await browser.newPage({ viewport: { width, height: 812 } });
  await page.setContent("<html><body style='margin:0'><div id='root'></div></body></html>");
  await page.addScriptTag({path:file});
  return page;
}
async function mount(page, rows) {
  await page.evaluate((data) => {
    const card = document.createElement("heating-scheduler-workflow-preview");
    window.testRequests = [];
    card.hass = {callWS: async request => {
      window.testRequests.push(request);
      return {response:{read_only:true,items:data}};
    }};
    card.setConfig({entry_id:"disposable_browser"});
    document.getElementById("root").append(card);
    window.testCard = card;
  }, rows);
  await page.waitForFunction(() => window.testCard?._loaded === true);
}
const samples = [
  {entity_id:"switch.schedule_weekday",title:"Morning heating",subtitle:"06:30 · 60 min · Mon, Tue",
   status:"Enabled",enabled:true,minutes:60,start:"06:30",weekdays:["mon","tue"],
   can_delete_after_confirmation:false},
  {entity_id:"switch.schedule_weekend",title:"Weekend heating",subtitle:"08:00 · 45 min · Sat, Sun",
   status:"Disabled",enabled:false,minutes:45,start:"08:00",weekdays:["sat","sun"],
   can_delete_after_confirmation:true},
];

test("375px Chromium navigation, state, disabled forms and no writes", async () => {
  const browser = await chromium.launch({headless:true});
  try {
    const page = await makePage(browser);
    await mount(page, samples);
    const root = page.locator("heating-scheduler-workflow-preview");
    assert.equal(await root.locator(".row").count(),2);
    await root.getByRole("button",{name:"Manage Schedules"}).click();
    assert.equal(await root.getByRole("button",{name:"🗑 Review"}).count(),1);
    await root.getByRole("button",{name:"🗑 Review"}).click();
    assert.equal(await root.getByRole("button",{name:"Confirm deletion — unavailable"}).isDisabled(),true);
    await root.getByRole("button",{name:"Cancel"}).click();
    await root.getByRole("button",{name:"✎ Edit"}).first().click();
    assert.equal(await root.getByRole("button",{name:"Save — unavailable"}).isDisabled(),true);
    assert.equal(await root.locator("fieldset input[type=checkbox]").count(),7);
    assert.equal(await root.locator("input:not([disabled])").count(),0);
    const requests=await page.evaluate(()=>window.testRequests);
    assert.equal(requests.length,1);
    assert.equal(requests[0].service,"list_schedules");
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth),true);
    await page.close();
  } finally {await browser.close();}
});

test("320px Chromium long names remain contained and status stays visible",async()=>{
  const browser=await chromium.launch({headless:true});
  try {
    const page=await makePage(browser,320);
    await mount(page,[{...samples[0],title:"Morning_".repeat(20)}]);
    const root=page.locator("heating-scheduler-workflow-preview");
    assert.equal(await root.locator(".status").count(),1);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth),true);
    await page.close();
  } finally {await browser.close();}
});

test("unknown state hides delete review even if flag is inconsistent",async()=>{
  const browser=await chromium.launch({headless:true});
  try{
    const page=await makePage(browser);
    await mount(page,[{...samples[1],status:"Unknown",can_delete_after_confirmation:true}]);
    const root=page.locator("heating-scheduler-workflow-preview");
    await root.getByRole("button",{name:"Manage Schedules"}).click();
    assert.equal(await root.getByRole("button",{name:"🗑 Review"}).count(),0);
    await page.close();
  }finally{await browser.close();}
});
