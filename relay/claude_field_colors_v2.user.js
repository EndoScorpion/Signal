// ==UserScript==
// @name         Claude Field Colors v2
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  Fixes field borders AND Claude icon visibility under black-green-2 high-contrast theme
// @match        https://claude.ai/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const GREEN = 'rgb(0,200,0)';
    const GREEN_DIM = 'rgba(0,200,0,0.4)';

    const css = `
        /* ─── FIELD BORDERS ─────────────────────────────────────────── */
        input,
        textarea,
        [contenteditable="true"],
        [role="textbox"] {
            border: 1px solid ${GREEN} !important;
            outline: none !important;
            box-shadow: 0 0 0 1px ${GREEN_DIM} !important;
        }
        input:focus,
        textarea:focus,
        [contenteditable="true"]:focus,
        [role="textbox"]:focus {
            border: 1.5px solid ${GREEN} !important;
            box-shadow: 0 0 4px 1px ${GREEN_DIM} !important;
        }

        /* Chat compose area */
        [data-testid="composer-container"],
        [class*="composer"],
        [class*="ProseMirror"],
        [class*="inputContainer"],
        [class*="input-container"] {
            border: 1px solid ${GREEN} !important;
        }

        /* Notifications / toasts */
        [role="alert"], [role="status"], [aria-live],
        [class*="toast"], [class*="Toast"],
        [class*="banner"], [class*="Banner"],
        [class*="notification"], [class*="Notification"],
        [class*="snackbar"], [class*="Snackbar"] {
            border: 1px solid ${GREEN} !important;
            box-shadow: 0 0 4px ${GREEN_DIM} !important;
        }

        /* Dialogs */
        [role="dialog"], [role="alertdialog"],
        [class*="modal"], [class*="Modal"],
        [class*="dialog"], [class*="Dialog"],
        [class*="popup"], [class*="Popup"] {
            border: 1px solid ${GREEN} !important;
            box-shadow: 0 0 6px 1px ${GREEN_DIM} !important;
        }

        /* Buttons */
        button, [role="button"],
        [type="button"], [type="submit"], [type="reset"],
        [class*="btn"], [class*="Btn"],
        [class*="button"], [class*="Button"] {
            border: 1px solid ${GREEN} !important;
        }
        button:hover, [role="button"]:hover {
            box-shadow: 0 0 4px ${GREEN_DIM} !important;
        }

        /* Dropdowns */
        select, [role="listbox"], [role="combobox"],
        [role="menu"], [class*="dropdown"], [class*="Dropdown"] {
            border: 1px solid ${GREEN} !important;
        }

        /* ─── CLAUDE ICON FIX ───────────────────────────────────────── */
        /* Prevent Windows High-Contrast from overriding SVG fill colors */
        [class*="claude-icon"] svg,
        [class*="claudeIcon"] svg,
        [aria-label*="Claude"] svg,
        header svg,
        nav svg,
        [class*="sidebar"] svg,
        [class*="Sidebar"] svg {
            forced-color-adjust: none !important;
            -webkit-forced-color-adjust: none !important;
            color-scheme: dark !important;
        }

        /* Claude logo / wordmark */
        [class*="logo"] svg *, [class*="Logo"] svg *,
        [class*="brand"] svg *, [class*="Brand"] svg *,
        [aria-label*="Claude"] svg path,
        [aria-label*="Claude"] svg rect,
        [aria-label*="Claude"] svg circle {
            forced-color-adjust: none !important;
        }

        /* All icon SVGs in buttons/nav */
        button svg, [role="button"] svg,
        nav svg, header svg {
            forced-color-adjust: none !important;
            -webkit-forced-color-adjust: none !important;
        }
    `;

    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);

    const observer = new MutationObserver(() => {
        if (!document.head.contains(style)) {
            document.head.appendChild(style);
        }
    });
    observer.observe(document.documentElement, { childList: true, subtree: false });
})();
