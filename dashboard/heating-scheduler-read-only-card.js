/* Heating Scheduler mobile list: read-only Lovelace custom card.
 * DEVELOPMENT PREVIEW. Does not call any switch, scheduler mutation or start service.
 */
class HeatingSchedulerReadOnlyCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
    this._loadedFor = null;
    this._loading = false;
    this._rows = null;
    this._error = null;
  }

  setConfig(config) {
    if (!config || typeof config.entry_id !== "string" || !config.entry_id.trim()) {
      throw new Error("Heating Scheduler: entry_id is required");
    }
    const previous = this._config?.entry_id;
    this._config = { entry_id: config.entry_id.trim(), title: config.title || "Heating Control" };
    if (previous !== this._config.entry_id) {
      this._loadedFor = null;
      this._rows = null;
    }
    this._render();
    this._refresh();
  }

  set hass(hass) {
    this._hass = hass;
    if (this._config && !this._loadedFor) this._refresh();
  }

  getCardSize() { return Math.max(2, (this._rows?.length || 0) + 1); }

  async _refresh(force = false) {
    if (!this._config || !this._hass || this._loading) return;
    const entryId = this._config.entry_id;
    if (!force && this._loadedFor === entryId) return;
    this._loading = true;
    this._error = null;
    this._render();
    try {
      // Home Assistant response services use the WebSocket call_service command.
      const result = await this._hass.callWS({
        type: "call_service",
        domain: "heating_scheduler",
        service: "list_schedules",
        service_data: { entry_id: entryId },
        return_response: true,
      });
      if (this._config.entry_id !== entryId) return;
      const payload = result?.response ?? result;
      if (!payload || payload.read_only !== true || !Array.isArray(payload.items)) {
        throw new Error("Unexpected read-only schedule response");
      }
      this._rows = payload.items;
      this._loadedFor = entryId;
    } catch (err) {
      if (this._config.entry_id === entryId) {
        this._error = String(err?.message || err || "Unable to load schedules");
      }
    } finally {
      this._loading = false;
      this._render();
    }
  }

  _render() {
    if (!this.shadowRoot || !this._config) return;
    const root = this.shadowRoot;
    root.replaceChildren();
    const style = document.createElement("style");
    style.textContent = `
      ha-card { padding: 16px; }
      .header { display:flex; justify-content:space-between; align-items:center; gap:12px; }
      h2 { font-size:18px; margin:0 0 8px; font-weight:600; }
      button { border:1px solid var(--divider-color); border-radius:12px;
        background:transparent; color:var(--primary-text-color); padding:8px 12px; cursor:pointer; }
      button:disabled { opacity:.5; cursor:default; }
      .item { display:flex; justify-content:space-between; gap:12px; align-items:center;
        padding:13px 0; border-top:1px solid var(--divider-color); }
      .title { font-weight:600; overflow-wrap:anywhere; }
      .subtitle { font-size:13px; margin-top:4px; color:var(--secondary-text-color); }
      .status { flex-shrink:0; font-size:12px; border-radius:14px; padding:5px 9px;
        color:var(--primary-text-color); background:var(--secondary-background-color); }
      .status.green { color:var(--success-color, green); }
      .message { padding:12px 0; color:var(--secondary-text-color); }
    `;
    const card = document.createElement("ha-card");
    const header = document.createElement("div");
    header.className = "header";
    const title = document.createElement("h2");
    title.textContent = this._config.title;
    const refresh = document.createElement("button");
    refresh.type = "button";
    refresh.textContent = "Refresh";
    refresh.disabled = this._loading;
    refresh.addEventListener("click", () => this._refresh(true));
    header.append(title, refresh);
    card.append(header);
    if (this._error) {
      const message = document.createElement("div");
      message.className = "message";
      message.textContent = this._error;
      card.append(message);
    } else if (this._loading && !this._rows) {
      const message = document.createElement("div");
      message.className = "message";
      message.textContent = "Loading schedules…";
      card.append(message);
    } else if (this._rows?.length) {
      for (const row of this._rows) {
        const item = document.createElement("div");
        item.className = "item";
        const details = document.createElement("div");
        const name = document.createElement("div");
        name.className = "title";
        name.textContent = String(row.title || "Unnamed schedule");
        const subtitle = document.createElement("div");
        subtitle.className = "subtitle";
        subtitle.textContent = String(row.subtitle || "");
        details.append(name, subtitle);
        const status = document.createElement("span");
        status.className = row.status_color === "green" ? "status green" : "status";
        status.textContent = ["Enabled", "Disabled", "Unknown"].includes(row.status)
          ? row.status : "Unknown";
        item.append(details, status);
        card.append(item);
      }
    } else {
      const message = document.createElement("div");
      message.className = "message";
      message.textContent = "No matching heating schedules";
      card.append(message);
    }
    root.append(style, card);
  }
}
if (!customElements.get("heating-scheduler-read-only-card")) {
  customElements.define("heating-scheduler-read-only-card", HeatingSchedulerReadOnlyCard);
}
