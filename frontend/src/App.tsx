import { useState } from 'react'
import axios from 'axios'
import Editor from './components/Editor'
import { Link, Sparkles, Loader2, AlertCircle } from 'lucide-react'

// Adjust base URL if needed (e.g., from environment variables)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://192.168.1.30:8001'

function App() {
    const [url, setUrl] = useState('')
    const [generating, setGenerating] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [mode, setMode] = useState<'note' | 'xhs'>('note')
    const [article, setArticle] = useState<{ title: string; content_html: string } | null>(null)

    const handleGenerate = async () => {
        if (!url) return
        if (!url.includes('propertyguru.com.sg')) {
            setError('请输入有效的 PropertyGuru 新加坡链接')
            return
        }

        setGenerating(true)
        setError(null)

        try {
            const response = await axios.post(`${API_BASE_URL}/api/generate`, { url, mode })
            setArticle(response.data)
        } catch (err: any) {
            console.error(err)
            setError(err.response?.data?.detail || '生成失败，请稍后重试。')
        } finally {
            setGenerating(false)
        }
    }

    return (
        <div className="min-h-screen bg-[#f8fafc] flex flex-col items-center py-12 px-4 sm:px-6">
            <div className="w-full max-w-4xl space-y-8">
                {/* Header */}
                <div className="text-center space-y-2">
                    <div className="inline-flex items-center justify-center p-2 bg-indigo-100 text-indigo-700 rounded-xl mb-4">
                        <Sparkles size={24} />
                    </div>
                    <h1 className="text-4xl font-bold tracking-tight text-slate-900">
                        PG to WeChat Note
                    </h1>
                    <p className="text-slate-500 text-lg">
                        瞬间将 PropertyGuru 房源转换成极其诱人的微信和红书图文。
                    </p>
                </div>

                {/* URL Input Area */}
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-col sm:flex-row gap-3">
                            <div className="relative flex-1">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                                    <Link size={18} />
                                </div>
                                <input
                                    type="text"
                                    value={url}
                                    onChange={(e) => setUrl(e.target.value)}
                                    placeholder="粘贴 PropertyGuru 房源链接..."
                                    className="block w-full pl-11 pr-4 py-3 bg-slate-50 border-transparent focus:bg-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent rounded-xl transition-all text-slate-900 placeholder:text-slate-400"
                                />
                            </div>
                            <button
                                onClick={handleGenerate}
                                disabled={generating || !url}
                                className={`px-8 py-3 font-semibold rounded-xl transition-all flex items-center justify-center gap-2 min-w-[140px] text-white ${mode === 'xhs' ? 'bg-rose-500 hover:bg-rose-600' : 'bg-slate-900 hover:bg-slate-800'
                                    }`}
                            >
                                {generating ? (
                                    <>
                                        <Loader2 className="animate-spin" size={20} />
                                        生成中...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles size={20} />
                                        智能生成
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Mode Selection */}
                        <div className="flex items-center gap-3">
                            <span className="text-sm font-medium text-slate-500">生成模式:</span>
                            <div className="flex bg-slate-100 p-1 rounded-lg">
                                <button
                                    onClick={() => setMode('note')}
                                    className={`px-4 py-1.5 rounded-md text-sm font-bold transition-all ${mode === 'note' ? 'bg-white text-indigo-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                                        }`}
                                >
                                    专业笔记
                                </button>
                                <button
                                    onClick={() => setMode('xhs')}
                                    className={`px-4 py-1.5 rounded-md text-sm font-bold transition-all ${mode === 'xhs' ? 'bg-white text-rose-500 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                                        }`}
                                >
                                    小红书
                                </button>
                            </div>
                        </div>
                    </div>

                    {error && (
                        <div className="mt-4 flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded-lg border border-red-100">
                            <AlertCircle size={18} />
                            <p className="text-sm font-medium">{error}</p>
                        </div>
                    )}
                </div>

                {/* Editor Area */}
                <div className="h-[700px]">
                    {article ? (
                        <Editor content={article.content_html} title={article.title} mode={mode} />
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center bg-slate-50 rounded-2xl border-2 border-dashed border-slate-200 text-slate-400 space-y-4">
                            <div className="p-4 bg-white rounded-full shadow-sm">
                                <Sparkles size={32} className="text-slate-300" />
                            </div>
                            <p className="font-medium">粘贴链接并点击“智能生成”开始</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Footer */}
            <footer className="mt-16 text-slate-400 text-sm">
                &copy; 2024 PG to WeChat Note SaaS · 专为新加坡房产经纪打造
            </footer>
        </div>
    )
}

export default App
