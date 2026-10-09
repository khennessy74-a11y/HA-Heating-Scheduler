# Mobile refresh and narrow-width protection

The read-only workflow preview now responds safely when a schedule changes
while a user is on the edit or deletion-review screen. A refresh updates the
selected row by its stable entity ID, leaves deletion review if its state is no
longer confirmed disabled, and returns to Heating Control if the schedule
disappears. The UI does **not** call delete or toggle services.

CSS now provides an explicit narrow-width layout at 420px with wrapped rows,
a four-column weekday grid and a 44px minimum height for navigation actions.

Node tests cover removal, disable-to-enable transitions and the responsive
style contract. These tests execute the dashboard logic in a fake DOM; actual
browser rendering and physical-device validation are still outstanding.
