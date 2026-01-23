---
sidebar_position: 2
---

# 🛠️ User Troubleshooting

Common issues and their quick solutions for teachers and administrators.

---

## 📤 Upload Issues

### "File format not supported"
- **Cause**: You uploaded a file with an extension other than `.csv`, `.xls`, or `.xlsx`.
- **Solution**: Save your Excel sheet as a **CSV (Comma Delimited)** file and try again.

### "Required columns missing"
- **Cause**: The system couldn't find "Roll No" or "Name".
- **Solution**: Ensure your spreadsheet has clear headers in the first row.

---

## 🎯 Algorithm & Validation

### "Critical Error: Classroom Overfilled"
- **Cause**: You have more students than available seats (after accounting for broken seats).
- **Solution**: 
  1. Reduce the number of students in the current batch.
  2. Increase the classroom dimensions (Rows/Cols).
  3. Repair "Broken Seats" in the visual editor.

### "Warning: Paper Set Sequence Gap"
- **Cause**: To respect physical distance or broken seats, the algorithm had to skip a student in the A/B alternation sequence.
- **Solution**: This is often safe to ignore. It just means the student sequence isn't perfectly alternating (e.g., A - [gap] - A).

---

## 🎨 UI & Display

### "Seating Grid looks distorted"
- **Cause**: Browser zoom or very large classroom dimensions (e.g., 50x50) on a small screen.
- **Solution**: 
  1. Use **Ctrl + 0** to reset browser zoom.
  2. Use the **Full Screen** toggle in the dashboard.

### "Dashboard is not loading"
- **Cause**: Local session data might be outdated.
- **Solution**: Perform a **Hard Refresh** (Ctrl + F5) or clear browser cache for this site.

---

## 🔑 Authentication

### "Session Expired"
- **Cause**: Your security token has timed out (usually after 24 hours).
- **Solution**: Log out and log back in. Your active plan progress is **saved automatically**.

---

:::tip Need more help?
Contact your department's technical coordinator or report a bug via the **Feedback** button in the sidebar.
:::
