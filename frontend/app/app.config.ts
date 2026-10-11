export default defineAppConfig({
  ui: {
    colors: {
      primary: 'gold',
      neutral: 'stone',
    },
    button: {
      slots: {
        base: 'uppercase tracking-[0.18em] text-xs',
      },
    },
    badge: {
      slots: {
        base: 'uppercase tracking-wider',
      },
    },
  },
})
