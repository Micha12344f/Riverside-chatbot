// @ts-check
/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Deep Chat',
  tagline: 'Fully customizable AI chat component',
  url: 'https://deepchat.dev',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.png',
  organizationName: 'OvidijusParsiunas',
  projectName: 'deep-chat',

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/OvidijusParsiunas/deep-chat/tree/main/website/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Deep Chat',
        logo: { alt: 'Deep Chat Logo', src: 'img/logo.png' },
        items: [
          { to: '/docs', label: 'Docs', position: 'left' },
          { to: '/examples', label: 'Examples', position: 'left' },
          { href: 'https://github.com/OvidijusParsiunas/deep-chat', label: 'GitHub', position: 'right' },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          { title: 'Docs', items: [{ label: 'Getting Started', to: '/docs' }] },
          { title: 'Community', items: [{ label: 'GitHub', href: 'https://github.com/OvidijusParsiunas/deep-chat' }] },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Deep Chat. Built with Docusaurus.`,
      },
    }),
};

module.exports = config;
