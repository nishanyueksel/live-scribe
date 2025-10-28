"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { ScrollArea } from "@/components/ui/scroll-area"
import { FileText, ArrowLeft, Download, AlertCircle } from "lucide-react"

interface TranscriptionData {
  transcript: string;
  summary: string;
  action_items: string[];
}

export default function ResultsPage() {
  const router = useRouter()
  const [transcriptionData, setTranscriptionData] = useState<TranscriptionData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [actionItemsStatus, setActionItemsStatus] = useState<{ [key: number]: boolean }>({})

  useEffect(() => {
    // Get transcription data from sessionStorage
    const storedData = sessionStorage.getItem("transcriptionData")
    if (storedData) {
      try {
        const data: TranscriptionData = JSON.parse(storedData)
        setTranscriptionData(data)
        // Initialize action items status (all unchecked initially)
        const initialStatus: { [key: number]: boolean } = {}
        data.action_items.forEach((_, index) => {
          initialStatus[index] = false
        })
        setActionItemsStatus(initialStatus)
      } catch (err) {
        console.error("Error parsing transcription data:", err)
        setError("Failed to load transcription data")
      }
    } else {
      setError("No transcription data found. Please upload and process an audio file first.")
    }
  }, [])

  const handleActionItemToggle = (index: number) => {
    setActionItemsStatus(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const handleExportPDF = async () => {
    if (!transcriptionData) return

    try {
      // Send POST request to backend to generate PDF
      const response = await fetch("http://127.0.0.1:8000/api/v1/export-pdf", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          transcript: transcriptionData.transcript,
          summary: transcriptionData.summary,
          action_items: transcriptionData.action_items,
        }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Get the PDF blob
      const blob = await response.blob()

      // Create download link
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.style.display = "none"
      a.href = url
      a.download = "meeting_transcript.pdf"
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

    } catch (err) {
      console.error("Error exporting PDF:", err)
      alert("Failed to export PDF. Please try again.")
    }
  }

  const handleBackToUpload = () => {
    // Clear sessionStorage when going back
    sessionStorage.removeItem("transcriptionData")
    router.push("/")
  }

  // Show error state if no data or error occurred
  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-center">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-700">{error}</p>
            </div>
            <Button
              onClick={handleBackToUpload}
              className="w-full mt-4"
              variant="outline"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Upload
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // Show loading state while data is being loaded
  if (!transcriptionData) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-4 border-gray-300 border-t-gray-900 rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading transcription results...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-2">Transcription Results</h1>
          <p className="text-muted-foreground">Your audio has been processed and analyzed</p>
        </div>

        {/* Transcript Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Transcript
            </CardTitle>
            <CardDescription>Full transcription of your audio file</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-64 w-full rounded-md border p-4">
              <div className="text-sm leading-relaxed whitespace-pre-line">{transcriptionData.transcript}</div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Summary Section */}
        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
            <CardDescription>Key points extracted from the conversation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-sm leading-relaxed whitespace-pre-line">{transcriptionData.summary}</div>
          </CardContent>
        </Card>

        {/* Action Items Section */}
        <Card>
          <CardHeader>
            <CardTitle>Action Items</CardTitle>
            <CardDescription>Tasks and follow-ups identified from the conversation</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {transcriptionData.action_items.map((item, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Checkbox
                    id={`item-${index}`}
                    checked={actionItemsStatus[index] || false}
                    onCheckedChange={() => handleActionItemToggle(index)}
                  />
                  <label
                    htmlFor={`item-${index}`}
                    className={`text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 ${
                      actionItemsStatus[index] ? 'line-through text-muted-foreground' : ''
                    }`}
                  >
                    {item}
                  </label>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button onClick={handleExportPDF} className="flex items-center gap-2">
            <Download className="h-4 w-4" />
            Export as PDF
          </Button>
          <Button variant="outline" onClick={handleBackToUpload} className="flex items-center gap-2 bg-transparent">
            <ArrowLeft className="h-4 w-4" />
            Back to Upload
          </Button>
        </div>
      </div>
    </div>
  )
}
