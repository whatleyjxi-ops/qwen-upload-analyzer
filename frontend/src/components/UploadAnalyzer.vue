<template>
  <main class="page-shell">
    <section class="chat-panel">
      <header class="panel-header">
        <div>
          <p class="eyebrow">Qwen Upload Analyzer</p>
          <h1>上传文件并分析</h1>
        </div>
        <button class="clear-button" type="button" :disabled="isLoading && !result" @click="clearResult">
          清空结果
        </button>
      </header>

      <section class="result-area" aria-live="polite">
        <div v-if="isLoading" class="loading-state">
          <span class="spinner" aria-hidden="true"></span>
          <div class="loading-copy">
            <strong>{{ loadingStage }}</strong>
            <span v-if="slowHint">{{ slowHint }}</span>
          </div>
        </div>

        <div v-else-if="error" class="message error-message">
          {{ error }}
        </div>

        <div v-else-if="result" class="message result-message">
          <div class="result-header">
            <div class="result-meta">
              <span>分析完成</span>
              <span>{{ categoryLabel(result.analysis.category) }}</span>
              <span>{{ result.analysis.file_count }} 个文件</span>
              <span>{{ result.analysis.mode === 'mock' ? 'Mock' : 'Qwen' }}</span>
              <span v-if="result.analysis.promptApplied">已应用后端预设提示词</span>
              <span v-if="result.analysis.promptVersion">promptVersion: {{ result.analysis.promptVersion }}</span>
            </div>
            <div class="result-actions">
              <span v-if="copyNotice" class="copy-notice" :class="{ 'copy-notice-error': copyFailed }">
                {{ copyNotice }}
              </span>
              <button type="button" :disabled="!hasAnalysisResult" @click="copyAnalysisResult">
                复制结果
              </button>
              <button type="button" :disabled="!hasAnalysisResult" @click="downloadAnalysis('md')">
                下载 MD
              </button>
              <button type="button" :disabled="!hasAnalysisResult" @click="downloadAnalysis('txt')">
                下载 TXT
              </button>
            </div>
          </div>
          <div v-if="debugTiming" class="timing-info">
            <span>保存耗时：{{ formatSeconds(debugTiming.saveSeconds) }}</span>
            <span v-if="debugTiming.ossSeconds > 0">OSS 上传耗时：{{ formatSeconds(debugTiming.ossSeconds) }}</span>
            <span>模型分析耗时：{{ formatSeconds(debugTiming.qwenSeconds) }}</span>
            <span>总耗时：{{ formatSeconds(debugTiming.totalSeconds) }}</span>
          </div>
          <div v-if="hasOssFile" class="debug-info">已使用 OSS 文件地址</div>
          <pre>{{ formattedAnalysisResult }}</pre>
        </div>

        <div v-else class="empty-state">
          <p>点击左下角加号上传文档、图片或视频。</p>
        </div>
      </section>

      <footer class="composer">
        <div class="upload-control">
          <button
            class="plus-button"
            type="button"
            :aria-expanded="isMenuOpen"
            aria-label="打开上传菜单"
            @click="isMenuOpen = !isMenuOpen"
          >
            +
          </button>

          <div v-if="isMenuOpen" class="upload-menu">
            <button type="button" @click="chooseUpload('document')">
              <span class="menu-icon">Doc</span>
              <span>
                <strong>上传文档</strong>
                <small>最多 1 个</small>
              </span>
            </button>
            <button type="button" @click="chooseUpload('image')">
              <span class="menu-icon">Img</span>
              <span>
                <strong>上传图片</strong>
                <small>最多 5 个，单个小于 100MB</small>
              </span>
            </button>
            <button type="button" @click="chooseUpload('video')">
              <span class="menu-icon">Vid</span>
              <span>
                <strong>上传视频</strong>
                <small>最多 1 个，单个小于 500MB</small>
              </span>
            </button>
          </div>
        </div>

        <div class="composer-copy">
          <strong>{{ activeConfig.title }}</strong>
          <span>{{ activeConfig.description }}</span>
        </div>
      </footer>

      <input
        ref="fileInput"
        class="sr-only"
        type="file"
        :accept="activeConfig.accept"
        :multiple="activeConfig.multiple"
        @change="handleFiles"
      />
    </section>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { analyzeUpload } from '../api/analyzeApi'

const MB = 1024 * 1024

const uploadConfigs = {
  document: {
    title: '文档分析',
    description: '支持单个文档上传。',
    accept: '.pdf,.doc,.docx,.txt,.md,.csv,.xlsx,.xls,.ppt,.pptx',
    multiple: false,
    maxFiles: 1,
    maxSize: Infinity,
  },
  image: {
    title: '图片分析',
    description: '最多 5 张图片，单张小于 100MB。',
    accept: 'image/*',
    multiple: true,
    maxFiles: 5,
    maxSize: 100 * MB,
  },
  video: {
    title: '视频分析',
    description: '单个视频小于 500MB，不限制时长。',
    accept: 'video/*',
    multiple: false,
    maxFiles: 1,
    maxSize: 500 * MB,
  },
}

const fileInput = ref(null)
const category = ref('document')
const isMenuOpen = ref(false)
const isLoading = ref(false)
const loadingStage = ref('正在上传文件...')
const slowHint = ref('')
const stageTimers = []
let copyNoticeTimer = 0
const error = ref('')
const result = ref(null)
const completedAt = ref('')
const copyNotice = ref('')
const copyFailed = ref(false)

const activeConfig = computed(() => uploadConfigs[category.value])
const debugTiming = computed(() => result.value?.debugTiming || null)
const hasOssFile = computed(() =>
  Boolean(result.value?.analysis?.files?.some((file) => file.ossUrl || file.signedUrl)),
)
const formattedAnalysisResult = computed(() => formatResultContent(result.value?.analysis?.result))
const hasAnalysisResult = computed(() => Boolean(result.value && formattedAnalysisResult.value))

function chooseUpload(nextCategory) {
  category.value = nextCategory
  isMenuOpen.value = false
  error.value = ''
  requestAnimationFrame(() => fileInput.value?.click())
}

async function handleFiles(event) {
  const files = Array.from(event.target.files || [])
  event.target.value = ''
  if (!files.length) return

  const validationError = validateSelectedFiles(files)
  if (validationError) {
    error.value = validationError
    result.value = null
    completedAt.value = ''
    return
  }

  isLoading.value = true
  error.value = ''
  result.value = null
  completedAt.value = ''
  clearCopyNotice()
  startStageTimers()

  try {
    result.value = await analyzeUpload(category.value, files)
    completedAt.value = new Date().toISOString()
    loadingStage.value = '分析完成'
  } catch (caughtError) {
    error.value = caughtError.message
  } finally {
    stopStageTimers()
    isLoading.value = false
  }
}

function validateSelectedFiles(files) {
  const config = activeConfig.value
  if (files.length > config.maxFiles) {
    return `${config.title}最多上传 ${config.maxFiles} 个文件。`
  }

  if (Number.isFinite(config.maxSize) && files.some((file) => file.size >= config.maxSize)) {
    return config.maxSize === 100 * MB ? '单个图片必须小于 100MB。' : '单个视频必须小于 500MB。'
  }

  return ''
}

function startStageTimers() {
  stopStageTimers()
  loadingStage.value = '正在上传文件...'
  slowHint.value = ''
  stageTimers.push(
    window.setTimeout(() => {
      loadingStage.value = '正在等待后端保存...'
    }, 600),
    window.setTimeout(() => {
      loadingStage.value = '正在分析中...'
    }, 1800),
    window.setTimeout(() => {
      slowHint.value = '视频文件较大，分析可能需要更久，请不要关闭页面。'
    }, 10000),
    window.setTimeout(() => {
      slowHint.value = '仍在分析中，长视频或大文件会消耗更长时间。'
    }, 30000),
  )
}

function stopStageTimers() {
  while (stageTimers.length) {
    window.clearTimeout(stageTimers.pop())
  }
}

function clearResult() {
  error.value = ''
  result.value = null
  completedAt.value = ''
  clearCopyNotice()
}

function formatSeconds(value) {
  const seconds = Number(value || 0)
  return `${seconds.toFixed(3)} 秒`
}

function categoryLabel(value) {
  return {
    image: '图片',
    video: '视频',
    document: '文档',
  }[value] || value
}

async function copyAnalysisResult() {
  if (!hasAnalysisResult.value) return

  try {
    await writeClipboard(formattedAnalysisResult.value)
    showCopyNotice('已复制', false)
  } catch {
    showCopyNotice('复制失败', true)
  }
}

async function writeClipboard(text) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }

  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.setAttribute('readonly', '')
  textarea.style.position = 'fixed'
  textarea.style.left = '-9999px'
  document.body.appendChild(textarea)
  textarea.select()
  const copied = document.execCommand('copy')
  document.body.removeChild(textarea)

  if (!copied) {
    throw new Error('copy failed')
  }
}

function downloadAnalysis(type) {
  if (!hasAnalysisResult.value) return

  const content = type === 'md' ? buildMarkdownContent() : buildTextContent()
  const mimeType = type === 'md' ? 'text/markdown;charset=utf-8' : 'text/plain;charset=utf-8'
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = buildDownloadFilename(type)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function buildDownloadFilename(type) {
  const analysis = result.value?.analysis || {}
  const safeCategory = (analysis.category || category.value || 'unknown').toString().replace(/[^a-z0-9_-]/gi, '-')
  return `qwen-analysis-${safeCategory}-${formatTimestampForFilename(new Date())}.${type}`
}

function buildMarkdownContent() {
  const analysis = result.value?.analysis || {}
  const lines = [
    '# Qwen 分析结果',
    '',
    `- 分析时间：${formatDisplayTime(completedAt.value)}`,
    `- 上传类型：${categoryLabel(analysis.category)}`,
    '',
    '## 文件列表',
    '',
    ...formatFileList(analysis.files, '- '),
    '',
    '## 分析结果正文',
    '',
    wrapMarkdownResult(formattedAnalysisResult.value),
  ]

  if (debugTiming.value) {
    lines.push('', '## debugTiming', '', '```json', JSON.stringify(debugTiming.value, null, 2), '```')
  }

  return `${lines.join('\n')}\n`
}

function buildTextContent() {
  const analysis = result.value?.analysis || {}
  const lines = [
    'Qwen 分析结果',
    '',
    `分析时间：${formatDisplayTime(completedAt.value)}`,
    `上传类型：${categoryLabel(analysis.category)}`,
    '',
    '文件列表：',
    ...formatFileList(analysis.files, ''),
    '',
    '分析结果正文：',
    formattedAnalysisResult.value,
  ]

  if (debugTiming.value) {
    lines.push('', 'debugTiming：', JSON.stringify(debugTiming.value, null, 2))
  }

  return `${lines.join('\n')}\n`
}

function formatFileList(files, prefix) {
  if (!Array.isArray(files) || files.length === 0) {
    return [`${prefix}无文件信息`]
  }

  return files.map((file, index) => {
    const name = file?.name || file?.filename || `文件 ${index + 1}`
    const url = file?.ossUrl || file?.signedUrl || file?.url || ''
    return `${prefix}${url ? `${name} (${url})` : name}`
  })
}

function formatResultContent(value) {
  if (value === null || value === undefined) return ''
  if (typeof value === 'object') return JSON.stringify(value, null, 2)
  const text = String(value)
  const trimmed = text.trim()
  if (!trimmed) return ''

  try {
    return JSON.stringify(JSON.parse(trimmed), null, 2)
  } catch {
    return text
  }
}

function wrapMarkdownResult(text) {
  const trimmed = text.trim()
  if (looksLikeJson(trimmed)) {
    return `\`\`\`json\n${trimmed}\n\`\`\``
  }
  return text.replaceAll('```', '\\`\\`\\`')
}

function looksLikeJson(text) {
  return (text.startsWith('{') && text.endsWith('}')) || (text.startsWith('[') && text.endsWith(']'))
}

function formatDisplayTime(value) {
  const date = value ? new Date(value) : new Date()
  return date.toLocaleString('zh-CN', { hour12: false })
}

function formatTimestampForFilename(date) {
  const pad = (value) => String(value).padStart(2, '0')
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    '-',
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join('')
}

function showCopyNotice(message, isError) {
  clearCopyNotice()
  copyNotice.value = message
  copyFailed.value = isError
  copyNoticeTimer = window.setTimeout(clearCopyNotice, 1800)
}

function clearCopyNotice() {
  if (copyNoticeTimer) {
    window.clearTimeout(copyNoticeTimer)
    copyNoticeTimer = 0
  }
  copyNotice.value = ''
  copyFailed.value = false
}
</script>
