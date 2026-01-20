// utils/colorUtils.js
export const toPrintFriendlyColor = (color) => {
  if (!color) return '#E5E7EB'; // Default light gray
  
  // If already a light color, return as-is
  // Otherwise, lighten it
  
  // Convert hex to RGB
  const hex = color.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  
  // Lighten by mixing with white (80% white, 20% original)
  const lightR = Math.round(r * 0.3 + 255 * 0.7);
  const lightG = Math.round(g * 0.3 + 255 * 0.7);
  const lightB = Math.round(b * 0.3 + 255 * 0.7);
  
  return `rgb(${lightR}, ${lightG}, ${lightB})`;
};

// Predefined print-friendly palette
export const PRINT_FRIENDLY_COLORS = {
  '#3b82f6': '#DBEAFE', // Blue → Light blue
  '#ef4444': '#FEE2E2', // Red → Light red
  '#22c55e': '#DCFCE7', // Green → Light green
  '#f97316': '#FFEDD5', // Orange → Light orange
  '#8b5cf6': '#EDE9FE', // Purple → Light purple
  '#ec4899': '#FCE7F3', // Pink → Light pink
  '#14b8a6': '#CCFBF1', // Teal → Light teal
  '#eab308': '#FEF9C3', // Yellow → Light yellow
};

export const getPrintFriendlyColor = (color) => {
  if (!color) return '#F3F4F6';
  
  // Check if we have a predefined mapping
  const lowerColor = color.toLowerCase();
  if (PRINT_FRIENDLY_COLORS[lowerColor]) {
    return PRINT_FRIENDLY_COLORS[lowerColor];
  }
  
  // Otherwise, auto-lighten
  return toPrintFriendlyColor(color);
};