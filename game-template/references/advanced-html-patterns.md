# 高级 HTML 模式（多帧视觉小说界面）

适用于每帧含有复杂数据的多帧翻页界面：多个媒体变量、多角色立绘、帧级副作用触发。

---

## Pattern 1：`#script-data` 隐藏容器

引擎将所有帧数据追加到隐藏的 `<div id="script-data">` 容器中。JS 在 `DOMContentLoaded` 时一次性解析为内存数组，翻页时只操作内存数组，不再逐行读取 `data-*` 属性。

适用场景：每帧有多个媒体变量、多角色立绘、副作用触发器。

**HTML 结构**：
```html
<div id="script-data" style="display:none">
  <!-- engine appends .frame divs here -->
</div>
```

每帧是一个 `.frame` div，带 `data-*` 属性和子元素：
```html
<div class="frame"
     data-speaker="Lando"
     data-bg-asset="[URL injected by engine]">
  <div class="characters-data"
       data-assets="[URL1],[URL2]"
       data-classes="fade-in,"></div>
  <div class="dialogue-content">dialogue text here</div>
</div>
```

**JS 启动时解析**：
```javascript
document.querySelectorAll('#script-data .frame').forEach(frameEl => {
  dialogueFrames.push({
    bgAsset: frameEl.dataset.bgAsset,
    speaker: frameEl.dataset.speaker,
    dialogue: frameEl.querySelector('.dialogue-content').textContent.trim(),
    characters: parseCharacters(frameEl)
  });
});
```

**变量替换规则**（追加每一帧）：
```toml
[[variable_replacement_rules]]
target_selector = "#script-data"
replacement_type = "append"
template = '<div class="frame" data-speaker="{{dialogue_list.speaker}}" data-bg-asset="{{dialogue_list.bg_asset}}"><div class="characters-data" data-assets="{{dialogue_list.portrait_asset}}"></div><div class="dialogue-content">{{dialogue_list.content}}</div></div>'
```

---

## Pattern 2：跨帧状态继承

渲染某帧时，只在该帧提供新值时才更新状态，否则沿用上一帧的值。这样 AI 只需在背景或角色发生变化时才输出对应字段。

```javascript
// 状态跨帧持久
let currentBg = '';
let currentChars = [];

function renderFrame(index) {
  const frame = dialogueFrames[index];
  if (frame.bgAsset) currentBg = frame.bgAsset;           // 无新值则继承
  if (frame.characters.length > 0) currentChars = frame.characters;  // 无新值则继承
  // 用 currentBg 和 currentChars 渲染
}
```

在 `response_format` 中，将 `bg_asset` 和 `portrait_asset` 标记为可选——AI 只在变化时输出。

---

## Pattern 3：帧级副作用（隐藏 input 触发器）

通过向隐藏 `<input>` 写值并调用 `.click()` 来触发引擎事件。适用于特定对话帧需要触发游戏引擎动作（添加联系人、添加日程等）的场景。

**HTML**：
```html
<!-- 隐藏触发器 -->
<input type="hidden" id="contact-trigger">
<input type="hidden" id="schedule-name">
<button id="trigger-add-schedule" style="display:none"></button>
```

帧数据中（通过变量替换注入）：
```html
data-contact-name="{{dialogue_list.contact_name}}"
data-schedule-name="{{dialogue_list.schedule_name}}"
```

JS 渲染帧时触发（用 `triggered` 标志防止重复触发）：
```javascript
if (frame.contactName && !frame.contactTriggered) {
  document.getElementById('contact-trigger').value = frame.contactName;
  document.getElementById('contact-trigger').click();
  frame.contactTriggered = true;  // 防止后退时重复触发
}
```

引擎监听 `#contact-trigger` 的 click 事件并读取其 value。

---

## Pattern 4：多角色立绘

用逗号分隔的素材 URL 和 CSS class 列表支持多角色同时显示。

**帧数据属性**：
```html
data-assets="[URL1],[URL2]"
data-classes="left fade-in, right"
```

**JS 解析与渲染**：
```javascript
const assets = frameEl.dataset.assets.split(',');
const classes = (frameEl.dataset.classes || '').split(',');
characters = assets.map((asset, i) => ({
  asset: asset.trim(),
  classes: (classes[i] || '').trim()
})).filter(c => c.asset);

// 渲染
charactersContainer.innerHTML = '';
currentChars.forEach(char => {
  charactersContainer.innerHTML += `<div class="character ${char.classes}"><img src="${char.asset}"></div>`;
});
```

**CSS 定位**：
```css
.character { position: absolute; bottom: 0; height: 80%; }
.character.left { left: 10%; }
.character.right { right: 10%; }
```
