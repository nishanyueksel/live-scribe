"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Upload, Loader2, AlertCircle } from "lucide-react"

interface TranscriptionResponse {
  transcript: string;
  summary: string;
  action_items: string[];
}

interface UploadResponse {
  job_id: string;
  filename: string;
  message: string;
}

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [transcriptText, setTranscriptText] = useState<string>("")
  const [isTranscribing, setIsTranscribing] = useState(false)
  const router = useRouter()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setError(null) // Clear any previous errors
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsProcessing(true)
    setIsTranscribing(false)
    setError(null)
    setTranscriptText("")

    try {
      // Step 1: Upload file and get job ID
      const formData = new FormData()
      formData.append("file", selectedFile)

      const uploadResponse = await fetch("http://127.0.0.1:8000/api/v1/upload", {
        method: "POST",
        body: formData,
      })

      if (!uploadResponse.ok) {
        throw new Error(`Upload failed! status: ${uploadResponse.status}`)
      }

      const uploadData: UploadResponse = await uploadResponse.json()
      console.log("File uploaded, job ID:", uploadData.job_id)

      setIsProcessing(false)
      setIsTranscribing(true)

      // Step 2: Start streaming transcription using EventSource
      const eventSource = new EventSource(`http://127.0.0.1:8000/api/v1/transcribe/${uploadData.job_id}`)

      let fullTranscript = ""

      eventSource.onmessage = (event) => {
        const data = event.data

        if (data === "[TRANSCRIPTION_COMPLETE]") {
          console.log("Transcription completed")
          setIsTranscribing(false)
          eventSource.close()

          // TODO: Add summary and action items extraction here
          // For now, navigate to results with just the transcript
          const transcriptionData: TranscriptionResponse = {
            transcript: fullTranscript,
            summary: "Summary will be added in future implementation",
            action_items: ["Action items will be added in future implementation"]
          }

          sessionStorage.setItem("transcriptionData", JSON.stringify(transcriptionData))
          router.push("/results")
          return
        }

        if (data.startsWith("[ERROR:")) {
          console.error("Transcription error:", data)
          setError(`Transcription error: ${data}`)
          setIsTranscribing(false)
          eventSource.close()
          return
        }

        // Regular transcript chunk
        fullTranscript += data + " "
        setTranscriptText(fullTranscript)
      }

      eventSource.onerror = (event) => {
        console.error("EventSource error:", event)
        setError("Connection error during transcription. Please try again.")
        setIsTranscribing(false)
        eventSource.close()
      }

    } catch (err) {
      console.error("Error uploading file:", err)
      setError(err instanceof Error ? err.message : "Failed to process the audio file. Please try again.")
      setIsProcessing(false)
      setIsTranscribing(false)
    }
  }

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Audio Transcription</CardTitle>
          <CardDescription>Upload your audio file to get started with transcription and summarization</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="audio-file">Select Audio File</Label>
            <p className="text-xs text-muted-foreground">
              Supported formats: MP3, WAV, M4A, OGG, FLAC
            </p>
            <Input
              id="audio-file"
              type="file"
              accept=".mp3,.wav,.m4a,.ogg,.flac"
              onChange={handleFileSelect}
              disabled={isProcessing}
            />
            {selectedFile && <p className="text-sm text-muted-foreground">Selected: {selectedFile.name}</p>}
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
              <AlertCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <Button onClick={handleUpload} disabled={!selectedFile || isProcessing || isTranscribing} className="w-full">
            {isProcessing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Uploading...
              </>
            ) : isTranscribing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Transcribing...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Upload & Process
              </>
            )}
          </Button>

          {isTranscribing && transcriptText && (
            <div className="space-y-2">
              <Label>Live Transcription:</Label>
              <div className="p-3 bg-gray-50 border rounded-md max-h-40 overflow-y-auto">
                <p className="text-sm whitespace-pre-wrap">{transcriptText}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
