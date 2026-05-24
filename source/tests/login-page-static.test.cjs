const fs = require('fs');
const path = require('path');
const assert = require('assert');

const htmlPath = path.join(__dirname, '..', 'frontend', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

function expectContains(label, needle) {
  assert(
    html.includes(needle),
    `${label}: expected frontend/index.html to contain ${JSON.stringify(needle)}`
  );
}

expectContains('title', '<title>基灵 · 公募基金 AI 营销平台</title>');
expectContains('login page shell', 'id="loginPage"');
expectContains('app shell gate', 'id="appShell"');
expectContains('brand english name', 'Fund Intelligence');
expectContains('brand slogan', '重新定义<span>AI时代下</span><br class="mobile-title-break">的基金营销新范式');
expectContains('brand capability line', '市场洞察.基金透视.AI素材生成');
expectContains('fund insight tile', '基金透视');
expectContains('fund checkup tile', '全方位体检');
expectContains('AI marketing material tile', 'AI营销素材');
expectContains('dynamic market size value', 'id="marketSizeValue"');
expectContains('dynamic market size period', 'id="marketSizePeriod">');
expectContains('stacked capability body', 'class="login-capability-body"');
expectContains('stacked market period style', '.login-capability-note');
expectContains('market period below value', 'display: block;');
expectContains('market period copy', 'periodEl.textContent = `（截至${result.data.period}）`;');
expectContains('dynamic market size loader', 'async function loadLoginMarketSize');
expectContains('login form', 'id="landingLoginForm"');
expectContains('trial button', 'id="landingTrialButton"');
expectContains('login submit handler', 'async function submitLandingLogin');
expectContains('landing login failure copy', "setLandingError('用户名或密码错误，请重新输入')");
expectContains('trial admin hint', '请联系管理员申请账号密码');
expectContains('auth status gate', 'function setAuthenticatedView');
expectContains('clear stale session on load', "fetch(`${AUTH_BASE}/logout`, { method: 'POST' })");
expectContains('register hidden', '联系管理员开通账号');
expectContains('motion reduction', '@media (prefers-reduced-motion: reduce)');
expectContains('curve logo', 'login-brand-mark');
expectContains('unauth hides product pages', 'body:not(.is-authenticated) [id^="page-"]');
expectContains('AI signal visual', 'login-signal-cluster');
expectContains('icon-first capability tiles', 'login-capability');

assert(
  !html.includes('switchToRegister()'),
  'register hidden: legacy switchToRegister link should not be shown'
);

assert(
  !html.includes('账号/密码：ai4leader'),
  'demo account hint should not be visible on the login page'
);

assert(
  !html.includes('AI READY') && !html.includes('login-ai-chip'),
  'AI READY chip should not be rendered'
);

assert(
  !html.includes('审核') &&
    !html.includes('待审核') &&
    !html.includes('驳回') &&
    !html.includes('提交人：张伟') &&
    !html.includes('id="audPanel"') &&
    !html.includes('id="page-audit"') &&
    !html.includes('approveContent') &&
    !html.includes('rejectContent'),
  'audit module should not be rendered'
);

assert(
  !html.includes('智能配图生成') &&
    !html.includes('AI 生成配图') &&
    !html.includes('id="imgCanvas"') &&
    !html.includes('function genImg') &&
    !html.includes('imgReady') &&
    !html.includes('打包下载（文案+图片）'),
  'image generation module should not be rendered in phase one'
);

assert(
  !html.includes('本周生成素材') &&
    !html.includes('合规通过率') &&
    !html.includes('平均生成时长') &&
    !html.includes('本月活跃用户') &&
    !html.includes('覆盖全销售渠道'),
  'generator dashboard stat cards should not be rendered'
);

assert(
  !html.includes('批量生成：效率提升利器') &&
    !html.includes('一次性选择多只基金，生成系列化营销内容') &&
    !html.includes('批量生成功能开发中'),
  'generator batch generation banner should not be rendered'
);

expectContains('AI workflow page shell', 'class="ai-workflow-page"');
expectContains('AI workflow taskbar', 'class="ai-workflow-taskbar"');
expectContains('fund context column', 'class="ai-context-column"');
expectContains('primary AI generation window', 'ai-generation-window');
expectContains('AI result column', 'class="ai-result-column"');
expectContains('AI generation window title', 'AI 生成窗口');
expectContains('current task focus', '当前任务：兴全合润混合 · 朋友圈文案');
expectContains('compliance rules enabled chip', '合规规则开启');
expectContains('AI result panel label', '生成结果');
expectContains('AI history panel label', '历史素材');
expectContains('my funds list container', 'id="myFundsList"');
expectContains('favorite state helper', 'function isFavoriteFund');
expectContains('favorite toggle helper', 'function toggleFavoriteFund');
expectContains('search favorite button', 'class="fund-fav-btn');
expectContains('selected fund favorite button', 'id="selectedFundFavoriteBtn"');
expectContains('add to own pool copy', '加自选');
expectContains('remove favorite button', 'removeFavoriteFund');
expectContains('remove favorite copy', '删除自选');
expectContains('fund market nav label', '基金市场');
expectContains('fund market page', 'id="page-dashboard"');
expectContains('fund market overview hook', 'id="marketOverviewCards"');
expectContains('fund market main chart', 'id="marketScaleChart"');
expectContains('fund company table', 'id="marketCompanyRows"');
expectContains('fund issuance chart', 'id="marketIssuanceChart"');
expectContains('fund market data loader', 'async function loadFundMarketPage');
expectContains('fund market data endpoint', '/fund/market-overview');
expectContains('fund market chart mode', 'function switchMarketChartMode');

const myFundsSection = html.slice(
  html.indexOf('PAGE: MY FUNDS'),
  html.indexOf('PAGE: BRAND')
);
assert(
  !myFundsSection.includes('⭐ 关注'),
  'my funds page should only show funds already in the user selected pool'
);

const generatorNavIndex = html.indexOf("switchPage('generator'");
const marketNavIndex = html.indexOf("switchPage('dashboard'");
const libraryNavIndex = html.indexOf("switchPage('library'");
assert(
  generatorNavIndex !== -1 && marketNavIndex !== -1 && libraryNavIndex !== -1 && generatorNavIndex < marketNavIndex && marketNavIndex < libraryNavIndex,
  'fund market should be the second main navigation item after generator'
);

console.log('login page static checks passed');
