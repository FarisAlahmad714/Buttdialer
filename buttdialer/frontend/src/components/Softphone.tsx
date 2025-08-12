import { useState, useEffect } from 'react'
import { PhoneIcon, PhoneXMarkIcon, MicrophoneIcon } from '@heroicons/react/24/solid'
import { twilioVoiceService } from '../services/twilioService'
import toast from 'react-hot-toast'

export default function Softphone() {
  const [isConnected, setIsConnected] = useState(false)
  const [callStatus, setCallStatus] = useState<string>('ready')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [isMuted, setIsMuted] = useState(false)

  useEffect(() => {
    // Initialize Twilio service
    twilioVoiceService.initialize((status, call) => {
      setCallStatus(status)
      setIsConnected(status === 'ready' || status === 'connected')
      
      if (status === 'incoming' && call) {
        toast(`Incoming call from ${call.parameters.From}`, {
          duration: 10000,
        })
      }
    })

    return () => {
      twilioVoiceService.disconnect()
    }
  }, [])

  const handleCall = async () => {
    if (!phoneNumber) {
      toast.error('Please enter a phone number')
      return
    }

    try {
      await twilioVoiceService.makeCall(phoneNumber)
      toast.success('Call initiated')
    } catch (error) {
      toast.error('Failed to make call')
    }
  }

  const handleHangup = () => {
    twilioVoiceService.hangup()
  }

  const handleAccept = () => {
    twilioVoiceService.acceptCall()
  }

  const handleReject = () => {
    twilioVoiceService.rejectCall()
  }

  const toggleMute = () => {
    if (isMuted) {
      twilioVoiceService.unmute()
    } else {
      twilioVoiceService.mute()
    }
    setIsMuted(!isMuted)
  }

  const getStatusColor = () => {
    switch (callStatus) {
      case 'ready': return 'bg-green-500'
      case 'connecting': return 'bg-yellow-500'
      case 'connected': return 'bg-blue-500'
      case 'incoming': return 'bg-purple-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col">
      {/* Status indicator */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
          <span className="text-sm font-medium text-gray-700 capitalize">
            {callStatus}
          </span>
        </div>
      </div>

      {/* Phone number input */}
      <div className="p-4 border-b border-gray-200">
        <input
          type="tel"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
          placeholder="Enter phone number"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          disabled={callStatus === 'connected' || callStatus === 'connecting'}
        />
      </div>

      {/* Call controls */}
      <div className="p-4 space-y-3">
        {callStatus === 'ready' && (
          <button
            onClick={handleCall}
            disabled={!phoneNumber || !isConnected}
            className="w-full flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PhoneIcon className="h-5 w-5 mr-2" />
            Call
          </button>
        )}

        {callStatus === 'incoming' && (
          <div className="space-y-2">
            <button
              onClick={handleAccept}
              className="w-full flex items-center justify-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              <PhoneIcon className="h-5 w-5 mr-2" />
              Accept
            </button>
            <button
              onClick={handleReject}
              className="w-full flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              <PhoneXMarkIcon className="h-5 w-5 mr-2" />
              Reject
            </button>
          </div>
        )}

        {(callStatus === 'connected' || callStatus === 'connecting') && (
          <div className="space-y-2">
            <button
              onClick={toggleMute}
              className={`w-full flex items-center justify-center px-4 py-2 rounded-md ${
                isMuted 
                  ? 'bg-yellow-600 text-white hover:bg-yellow-700' 
                  : 'bg-gray-600 text-white hover:bg-gray-700'
              }`}
            >
              <MicrophoneIcon className="h-5 w-5 mr-2" />
              {isMuted ? 'Unmute' : 'Mute'}
            </button>
            <button
              onClick={handleHangup}
              className="w-full flex items-center justify-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              <PhoneXMarkIcon className="h-5 w-5 mr-2" />
              Hang Up
            </button>
          </div>
        )}
      </div>

      {/* Call history/info would go here */}
      <div className="flex-1 p-4">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Recent Calls</h3>
        <div className="text-sm text-gray-500">
          No recent calls
        </div>
      </div>
    </div>
  )
}