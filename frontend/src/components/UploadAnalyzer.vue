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
          <span>正在分析...</span>
        </div>

        <div v-else-if="error" class="message error-message">
          {{ error }}
        </div>

        <div v-else-if="result" class="message result-message">
          <div class="result-meta">
            <span>{{ categoryLabel(result.analysis.category) }}</span>
            <span>{{ result.analysis.file_count }} 个文件</span>
            <span>{{ result.analysis.mode === 'mock' ? 'Mock' : 'Qwen' }}</span>
          </div>
          <div v-if="hasOssFile" class="debug-info">已使用 OSS 文件地址</div>
          <pre>{{ result.analysis.result }}</pre>
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
const error = ref('')
const result = ref(null)

const activeConfig = computed(() => uploadConfigs[category.value])
const hasOssFile = computed(() =>
  Boolean(result.value?.analysis?.files?.some((file) => file.ossUrl || file.signedUrl)),
)

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
    return
  }

  isLoading.value = true
  error.value = ''
  result.value = null

  try {
    result.value = await analyzeUpload(category.value, files)
  } catch (caughtError) {
    error.value = caughtError.message
  } finally {
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

function clearResult() {
  error.value = ''
  result.value = null
}

function categoryLabel(value) {
  return {
    image: '图片',
    video: '视频',
    document: '文档',
  }[value] || value
}
</script>
