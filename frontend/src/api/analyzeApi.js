export async function analyzeUpload(category, files) {
  const formData = new FormData()
  formData.append('category', category)

  Array.from(files).forEach((file) => {
    formData.append('files', file)
  })

  const response = await fetch('/api/analyze/upload', {
    method: 'POST',
    body: formData,
  })

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(payload.detail || '分析失败，请稍后重试。')
  }

  return payload
}
