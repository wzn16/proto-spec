/* ============================================================
   proto-spec 交互脚本 app.js —— 零依赖，全站统一引入
   ------------------------------------------------------------
   引入方式：<script defer src="../assets/app.js"></script>
   所有交互通过 data-action 声明在标签上，页面无需再写 JS：

     open-modal      data-target="#弹窗选择器"    打开弹窗
     close-modal     data-target="#弹窗选择器"    关闭弹窗
     open-drawer     data-target="#抽屉选择器"    打开抽屉
     close-drawer    data-target="#抽屉选择器"    关闭抽屉
     toggle-dropdown                              切换触发器的下一个兄弟菜单
     switch-tab      data-target="#面板id"        切换 .c-tabs 内页签
     toggle-collapse data-target="#折叠区选择器"  折叠 / 展开
     show-toast      data-message="提示文字"      底部提示，2.5 秒自动移除

   滚动锁定约定：弹窗 / 抽屉打开期间给 body 加 is-locked 类；
   该类需在 components.css 中定义（.is-locked { overflow: hidden; }），
   本文件只负责加 / 减类，不写任何内联样式。
   ============================================================ */
(function () {
  'use strict';

  /** 已打开浮层栈：[{ el, trigger }]，后开在上，ESC 只关最上层 */
  var overlayStack = [];

  /** 按选择器查元素（可传根节点），查不到返回 null */
  function query(selector, root) {
    return (root || document).querySelector(selector);
  }

  /** 在浮层栈中按元素定位条目 */
  function findEntry(el) {
    for (var i = 0; i < overlayStack.length; i++) {
      if (overlayStack[i].el === el) return overlayStack[i];
    }
    return null;
  }

  /** 同步滚动锁定：仅弹窗 / 抽屉算阻挡层，下拉菜单不锁滚动 */
  function syncBodyLock() {
    var blocking = overlayStack.some(function (entry) {
      return entry.el.classList.contains('c-modal') ||
        entry.el.classList.contains('c-drawer');
    });
    document.body.classList.toggle('is-locked', blocking);
  }

  /** 打开浮层：显示并压栈（同一浮层重复打开只记一次） */
  function openOverlay(el, trigger) {
    if (!findEntry(el)) overlayStack.push({ el: el, trigger: trigger });
    el.hidden = false;
    syncBodyLock();
  }

  /** 关闭浮层：隐藏并出栈；下拉菜单同步触发器 aria-expanded */
  function closeOverlay(el) {
    var entry = findEntry(el);
    el.hidden = true;
    if (!entry) return;
    overlayStack.splice(overlayStack.indexOf(entry), 1);
    if (entry.trigger && entry.trigger.hasAttribute('aria-expanded')) {
      entry.trigger.setAttribute('aria-expanded', 'false');
    }
    syncBodyLock();
  }

  /** 弹窗 / 抽屉开关：data-target 指向浮层根节点，open 决定开或关 */
  function setLayer(trigger, open) {
    var el = query(trigger.getAttribute('data-target') || '');
    if (!el) return;
    if (open) openOverlay(el, trigger);
    else closeOverlay(el);
  }

  /** 下拉菜单：约定菜单元素紧邻触发器（下一个兄弟节点） */
  function toggleDropdown(trigger) {
    var menu = trigger.nextElementSibling;
    if (!menu) return;
    if (menu.hidden) {
      menu.hidden = false;
      trigger.setAttribute('aria-expanded', 'true');
      if (!findEntry(menu)) overlayStack.push({ el: menu, trigger: trigger });
    } else {
      closeOverlay(menu);
    }
  }

  /** 页签：同组 .c-tabs__tab 只保留当前 --active，面板只显示目标 */
  function switchTab(trigger) {
    var panelId = trigger.getAttribute('data-target') || '';
    var group = trigger.closest('.c-tabs');
    if (!group || !panelId) return;
    var tabs = group.querySelectorAll('.c-tabs__tab');
    for (var i = 0; i < tabs.length; i++) {
      var active = tabs[i] === trigger;
      tabs[i].classList.toggle('c-tabs__tab--active', active);
      tabs[i].setAttribute('aria-selected', active ? 'true' : 'false');
    }
    var panels = group.querySelectorAll('.c-tabs__panel');
    for (var j = 0; j < panels.length; j++) {
      panels[j].hidden = ('#' + panels[j].id) !== panelId;
    }
  }

  /** 折叠区：直接切换目标元素的 hidden */
  function toggleCollapse(trigger) {
    var el = query(trigger.getAttribute('data-target') || '');
    if (el) el.hidden = !el.hidden;
  }

  /** 底部提示：创建 .c-toast，2.5 秒后自动移除 */
  function showToast(trigger) {
    var toast = document.createElement('div');
    toast.className = 'c-toast';
    toast.setAttribute('role', 'status');
    toast.textContent = trigger.getAttribute('data-message') || '操作成功';
    document.body.appendChild(toast);
    window.setTimeout(function () {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 2500);
  }

  /** 动作注册表：data-action 取值 → 处理函数 */
  var actions = {
    'open-modal': function (t) { setLayer(t, true); },
    'close-modal': function (t) { setLayer(t, false); },
    'open-drawer': function (t) { setLayer(t, true); },
    'close-drawer': function (t) { setLayer(t, false); },
    'toggle-dropdown': toggleDropdown,
    'switch-tab': switchTab,
    'toggle-collapse': toggleCollapse,
    'show-toast': showToast
  };

  /** document 级 click 委托：就近找 [data-action] 统一分发 */
  document.addEventListener('click', function (event) {
    var node = event.target;
    if (!node || typeof node.closest !== 'function') return;
    var trigger = node.closest('[data-action]');
    if (!trigger) return;
    var handler = actions[trigger.getAttribute('data-action')];
    if (handler) handler(trigger);
  });

  /** ESC：一次只关最上层浮层（弹窗 / 抽屉 / 下拉菜单统一入栈） */
  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Escape') return;
    var top = overlayStack[overlayStack.length - 1];
    if (top) closeOverlay(top.el);
  });
})();
