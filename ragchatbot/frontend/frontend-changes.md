# Frontend Changes: Theme Toggle Button

## Overview
Added a theme toggle button positioned in the top-right corner of the application with sun/moon icon design that switches between dark and light themes with smooth transition animations.

## Files Modified

### index.html
- Added a toggle button element with id `themeToggle` before the main container
- Includes two SVG icons (sun and moon) for visual state indication
- Button has proper accessibility attributes (`aria-label`, `title`)

### style.css

**Toggle Button Styles:**
- Added `.theme-toggle` class with fixed positioning (top-right corner)
- Circular button design (44x44px) matching the existing aesthetic
- Smooth hover effects with scale transform and border color change
- Focus states for keyboard accessibility (`:focus` and `:focus-visible`)
- Active state with press-down animation
- Icon transition animations (rotate and scale with 0.3s ease)

**Light Theme:**
- Added `[data-theme="light"]` selector with light theme CSS variables:
  - `--background: #f8fafc` (light gray-blue)
  - `--surface: #ffffff` (white)
  - `--surface-hover: #f1f5f9` (light hover)
  - `--text-primary: #1e293b` (dark text)
  - `--text-secondary: #64748b` (muted text)
  - `--border-color: #e2e8f0` (light borders)
  - `--assistant-message: #f1f5f9` (light message bubbles)

**Smooth Transitions:**
- Added 0.3s ease transitions on body and key UI elements for smooth theme switching
- Elements with transitions: sidebar, chat area, inputs, buttons, messages

### script.js

**Theme Functions:**
- `initThemeToggle()` - Loads saved theme from localStorage on page load
- `handleThemeToggle()` - Toggles between dark and light themes
- `applyTheme(theme)` - Applies theme by setting `data-theme` attribute on document element

**Features:**
- Theme persists across page reloads via localStorage (key: `theme`)
- Dynamic ARIA labels update based on current theme
- Keyboard support for Enter and Space keys

## Features Summary
- Dark/light theme switching
- Icon-based design with sun/moon icons
- Positioned in top-right corner (fixed position)
- Smooth color transitions (0.3s) when switching themes
- Smooth icon rotation and scale animations on toggle
- Hover effects with scale and glow
- Keyboard accessible (Tab, Enter, Space)
- ARIA attributes for screen reader support
- Theme persistence via localStorage
