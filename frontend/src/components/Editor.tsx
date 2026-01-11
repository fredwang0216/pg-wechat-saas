import React, { useEffect, useState } from 'react'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Typography from '@tiptap/extension-typography'
import Placeholder from '@tiptap/extension-placeholder'
import { Bold, List, ListOrdered, Heading2, Clipboard, Check, Image as ImageIcon, Loader2 } from 'lucide-react'

interface EditorProps {
    content: string
    title: string
    mode: 'note' | 'xhs'
}

const Editor: React.FC<EditorProps> = ({ content, title, mode }) => {
    const [copied, setCopied] = useState(false)
    const [generatingPoster, setGeneratingPoster] = useState(false)

    const editor = useEditor({
        extensions: [
            StarterKit,
            Typography,
            Image.configure({
                inline: false,
                allowBase64: true,
            }),
        ],
        content: content,
        editorProps: {
            attributes: {
                class: 'prose prose-slate max-w-none focus:outline-none min-h-[400px] p-6 text-slate-700',
            },
        },
    })

    useEffect(() => {
        if (editor && content) {
            editor.commands.setContent(content)
        }
    }, [content, editor])

    const copyRichText = async () => {
        if (!editor) return

        const html = editor.getHTML()

        try {
            const container = document.createElement('div')
            container.innerHTML = html
            container.style.position = 'fixed'
            container.style.left = '-9999px'
            container.style.top = '0'
            document.body.appendChild(container)

            const range = document.createRange()
            range.selectNodeContents(container)
            const selection = window.getSelection()
            if (selection) {
                selection.removeAllRanges()
                selection.addRange(range)
                document.execCommand('copy')
                setCopied(true)
                setTimeout(() => setCopied(false), 2000)
                selection.removeAllRanges()
            }
            document.body.removeChild(container)
        } catch (err) {
            console.error('Failed to copy: ', err)
            alert('复制失败，请尝试手动复制。')
        }
    }

    const generatePoster = async () => {
        if (!editor || !title) return
        setGeneratingPoster(true)

        try {
            const response = await fetch('http://localhost:8001/api/generate-poster', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    html: editor.getHTML(),
                    title: title
                }),
            })

            if (!response.ok) throw new Error('Poster generation failed')

            const blob = await response.blob()
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_poster.png`
            document.body.appendChild(a)
            a.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
        } catch (err) {
            console.error('Poster Error:', err)
            alert('生成海报失败，请重试。')
        } finally {
            setGeneratingPoster(false)
        }
    }

    if (!editor) return null

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden h-full flex flex-col">
            {/* Toolbar */}
            <div className="bg-slate-50 border-b border-slate-200 p-2 flex flex-col sm:flex-row items-center justify-between gap-2 overflow-x-auto">
                <div className="flex items-center gap-1">
                    <button
                        onClick={() => editor.chain().focus().toggleBold().run()}
                        className={`p-2 rounded-lg transition-all ${editor.isActive('bold') ? 'bg-indigo-100 text-indigo-700' : 'text-slate-500 hover:bg-slate-200 hover:text-slate-700'}`}
                        title="加粗"
                    >
                        <Bold size={18} />
                    </button>
                    <button
                        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                        className={`p-2 rounded-lg transition-all ${editor.isActive('heading', { level: 2 }) ? 'bg-indigo-100 text-indigo-700' : 'text-slate-500 hover:bg-slate-200 hover:text-slate-700'}`}
                        title="标题"
                    >
                        <Heading2 size={18} />
                    </button>
                    <div className="w-px h-6 bg-slate-200 mx-1" />
                    <button
                        onClick={() => editor.chain().focus().toggleBulletList().run()}
                        className={`p-2 rounded-lg transition-all ${editor.isActive('bulletList') ? 'bg-indigo-100 text-indigo-700' : 'text-slate-500 hover:bg-slate-200 hover:text-slate-700'}`}
                        title="无序列表"
                    >
                        <List size={18} />
                    </button>
                    <button
                        onClick={() => editor.chain().focus().toggleOrderedList().run()}
                        className={`p-2 rounded-lg transition-all ${editor.isActive('orderedList') ? 'bg-indigo-100 text-indigo-700' : 'text-slate-500 hover:bg-slate-200 hover:text-slate-700'}`}
                        title="有序列表"
                    >
                        <ListOrdered size={18} />
                    </button>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={generatePoster}
                        disabled={generatingPoster}
                        className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 font-bold rounded-xl transition-all disabled:opacity-50 shadow-sm"
                    >
                        {generatingPoster ? <Loader2 size={16} className="animate-spin" /> : <ImageIcon size={16} />}
                        {generatingPoster ? '渲染中...' : '生成长图'}
                    </button>

                    <button
                        onClick={copyRichText}
                        className={`flex items-center gap-2 px-6 py-2 rounded-xl font-bold transition-all shadow-sm text-white ${copied ? 'bg-green-500' : (mode === 'xhs' ? 'bg-rose-500 hover:bg-rose-600' : 'bg-indigo-600 hover:bg-indigo-700')
                            }`}
                    >
                        {copied ? <Check size={18} /> : <Clipboard size={18} />}
                        {copied ? '已复制' : '复制富文本'}
                    </button>
                </div>
            </div>

            {/* Editor Content */}
            <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200">
                <EditorContent editor={editor} />
            </div>
        </div>
    )
}

export default Editor
