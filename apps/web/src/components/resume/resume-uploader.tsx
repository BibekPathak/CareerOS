"use client"

import { useState, useRef, DragEvent } from "react"
import { Upload, File, X, CheckCircle2, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { api } from "@/lib/api-client"

interface ResumeUploaderProps {
  onUploadComplete: (result: { id: string }) => void
}

export function ResumeUploader({ onUploadComplete }: ResumeUploaderProps) {
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (f: File) => {
    if (!f.name.endsWith(".pdf")) {
      setError("Only PDF files are supported")
      return
    }
    setFile(f)
    setError(null)
    setUploading(true)
    try {
      const result = await api.uploadResume(f)
      setSuccess(true)
      onUploadComplete(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed")
    } finally {
      setUploading(false)
    }
  }

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
  }

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = () => setDragOver(false)

  const reset = () => {
    setFile(null)
    setError(null)
    setSuccess(false)
  }

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onClick={() => !uploading && !success && inputRef.current?.click()}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 transition-colors",
        dragOver && "border-primary bg-primary/5",
        success && "border-emerald-500/50 bg-emerald-500/5",
        error && "border-red-500/50 bg-red-500/5",
        !dragOver && !success && !error && "border-border hover:border-muted-foreground/50"
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />

      {uploading ? (
        <>
          <Loader2 className="h-10 w-10 animate-spin text-primary mb-3" />
          <p className="text-sm font-medium">Uploading and parsing...</p>
          <p className="text-xs text-muted-foreground mt-1">{file?.name}</p>
        </>
      ) : success ? (
        <>
          <CheckCircle2 className="h-10 w-10 text-emerald-400 mb-3" />
          <p className="text-sm font-medium text-emerald-400">Resume parsed successfully</p>
          <p className="text-xs text-muted-foreground mt-1">{file?.name}</p>
          <button
            onClick={(e) => { e.stopPropagation(); reset() }}
            className="mt-3 text-xs text-muted-foreground hover:text-foreground underline"
          >
            Upload different resume
          </button>
        </>
      ) : (
        <>
          <Upload className="h-10 w-10 text-muted-foreground mb-3" />
          <p className="text-sm font-medium">
            {dragOver ? "Drop your resume here" : "Upload your resume"}
          </p>
          <p className="text-xs text-muted-foreground mt-1">PDF format only</p>
          {error && <p className="text-xs text-red-400 mt-2">{error}</p>}
        </>
      )}
    </div>
  )
}
