/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'chaos-dark': '#1a1a1a',
                'chaos-red': '#dc2626',
                'chaos-gold': '#d97706',
                'chaos-blue': '#2563eb',
                'chaos-green': '#059669',
                'chaos-purple': '#7c3aed'
            },
            fontFamily: {
                'serif': ['Georgia', 'serif'],
                'display': ['Cinzel', 'serif']
            }
        },
    },
    plugins: [],
}