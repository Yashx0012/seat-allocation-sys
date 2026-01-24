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
  '#3b82f6': '#BFDBFE', // Standard Blue → Light Blue (Tailwind 200)
  '#ef4444': '#FECACA', // Standard Red → Light Red
  '#22c55e': '#BBF7D0', // Standard Green → Light Green
  '#f97316': '#FED7AA', // Standard Orange → Light Orange
  '#8b5cf6': '#E9D5FF', // Standard Purple → Light Purple
  '#ec4899': '#FBCFE8', // Standard Pink → Light Pink
  '#14b8a6': '#99F6E4', // Standard Teal → Light Teal
  '#eab308': '#FDE68A', // Standard Yellow → Light Yellow
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