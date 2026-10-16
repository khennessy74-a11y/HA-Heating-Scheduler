const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { chromium } = require('playwright');
const fixture = JSON.parse(fs.readFileSync(__dirname + '/portable-layout.json', 'utf8'));

test('iPhone-sized layout keeps action controls clear of labels', async () => {
  const browser = await chromium.launch({headless: true});
  try {
    for (const width of [320, 375, 390, 430, 768]) {
      const page = await browser.newPage({viewport:{width,height:800}});
      for (const [name, layout] of Object.entries(fixture)) {
        assert.equal(layout.field_area, layout.field, 'Action field must use its own grid area');
        if (name === 'manage-schedules') assert.equal(layout.mobile_columns, '1fr');
        await page.setContent('<main id="grid"><div id="icon">◷</div><div id="title">Long morning heating schedule name</div><div id="label">1 hour 30 minutes · Monday, Tuesday, Wednesday<br>● Enabled</div><button id="action">✎</button></main>');
        const css = [
          '* { box-sizing:border-box } body { margin:0;padding:8px;font:14px sans-serif }',
          '#grid { width:' + (width <= 430 ? 170 : 350) + 'px; display:grid;',
          'grid-template-areas:' + layout.areas + ';',
          'grid-template-columns:' + layout.columns + ';',
          'grid-template-rows:' + layout.rows + ';',
          'row-gap:' + layout.gap + ';min-height:' + layout.min_height + ';padding:10px;border:1px solid #888; }',
          '#icon {grid-area:i;text-align:center}',
          '#title {grid-area:n;text-align:center;overflow-wrap:anywhere}',
          '#label {grid-area:l;text-align:center;overflow-wrap:anywhere}',
          '#action {grid-area:' + layout.field_area + ';height:32px;width:32px;justify-self:end}'
        ].join('\n');
        await page.addStyleTag({content:css});
        const boxes = await page.evaluate(() => {
          const rect = id => {
            const r=document.getElementById(id).getBoundingClientRect();
            return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width};
          };
          return {action:rect('action'),label:rect('label'),title:rect('title'),grid:rect('grid')};
        });
        const overlaps=(a,b)=>a.left<b.right && b.left<a.right && a.top<b.bottom && b.top<a.bottom;
        assert.equal(overlaps(boxes.action,boxes.label),false,name+' action-label overlap at '+width);
        assert.equal(overlaps(boxes.action,boxes.title),false,name+' action-title overlap at '+width);
        assert.ok(boxes.action.right<=boxes.grid.right && boxes.action.left>=boxes.grid.left);
        const gridStyle = await page.locator('#grid').evaluate(el => getComputedStyle(el).gridTemplateAreas);
        assert.ok(gridStyle.includes(layout.field_area), name + ' action area missing in computed CSS');
        await page.locator('#action').click();
        console.log('PASS '+name+' viewport '+width + ' action remains clickable');
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }
});
