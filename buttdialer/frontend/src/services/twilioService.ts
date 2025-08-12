import { Device, Call } from '@twilio/voice-sdk'
import api from './api'
import toast from 'react-hot-toast'

class TwilioVoiceService {
  private device: Device | null = null
  private activeCall: Call | null = null
  private onCallStatusChange?: (status: string, call?: Call) => void

  async initialize(onCallStatusChange?: (status: string, call?: Call) => void) {
    this.onCallStatusChange = onCallStatusChange
    
    try {
      // Get access token from backend
      const response = await api.get('/calls/token')
      const { token } = response.data

      // Initialize Twilio Device
      this.device = new Device(token, {
        logLevel: 1,
        allowIncomingWhileBusy: false,
      })

      // Set up event listeners
      this.setupEventListeners()

      // Register the device
      await this.device.register()
      
      toast.success('Softphone connected')
      this.onCallStatusChange?.('ready')
      
    } catch (error) {
      console.error('Failed to initialize Twilio device:', error)
      toast.error('Failed to connect softphone')
      this.onCallStatusChange?.('error')
    }
  }

  private setupEventListeners() {
    if (!this.device) return

    this.device.on('registered', () => {
      console.log('Device registered')
      this.onCallStatusChange?.('ready')
    })

    this.device.on('error', (error) => {
      console.error('Device error:', error)
      toast.error('Softphone error occurred')
      this.onCallStatusChange?.('error')
    })

    this.device.on('incoming', (call) => {
      console.log('Incoming call from:', call.parameters.From)
      this.activeCall = call
      this.onCallStatusChange?.('incoming', call)
      
      // Set up call event listeners
      this.setupCallEventListeners(call)
    })

    this.device.on('tokenWillExpire', async () => {
      try {
        const response = await api.get('/calls/token')
        const { token } = response.data
        this.device?.updateToken(token)
      } catch (error) {
        console.error('Failed to refresh token:', error)
      }
    })
  }

  private setupCallEventListeners(call: Call) {
    call.on('accept', () => {
      console.log('Call accepted')
      this.onCallStatusChange?.('connected', call)
    })

    call.on('disconnect', () => {
      console.log('Call ended')
      this.activeCall = null
      this.onCallStatusChange?.('ready')
    })

    call.on('cancel', () => {
      console.log('Call cancelled')
      this.activeCall = null
      this.onCallStatusChange?.('ready')
    })

    call.on('reject', () => {
      console.log('Call rejected')
      this.activeCall = null
      this.onCallStatusChange?.('ready')
    })

    call.on('error', (error) => {
      console.error('Call error:', error)
      this.activeCall = null
      this.onCallStatusChange?.('error')
    })
  }

  async makeCall(phoneNumber: string) {
    if (!this.device) {
      throw new Error('Device not initialized')
    }

    if (this.activeCall) {
      throw new Error('Already on a call')
    }

    try {
      const call = await this.device.connect({
        params: {
          To: phoneNumber
        }
      })

      this.activeCall = call
      this.setupCallEventListeners(call)
      this.onCallStatusChange?.('connecting', call)

      return call
    } catch (error) {
      console.error('Failed to make call:', error)
      throw error
    }
  }

  acceptCall() {
    if (this.activeCall) {
      this.activeCall.accept()
    }
  }

  rejectCall() {
    if (this.activeCall) {
      this.activeCall.reject()
    }
  }

  hangup() {
    if (this.activeCall) {
      this.activeCall.disconnect()
    }
  }

  mute() {
    if (this.activeCall) {
      this.activeCall.mute(true)
    }
  }

  unmute() {
    if (this.activeCall) {
      this.activeCall.mute(false)
    }
  }

  isMuted(): boolean {
    return this.activeCall?.isMuted() || false
  }

  getCallStatus(): string {
    return this.activeCall?.status() || 'ready'
  }

  isConnected(): boolean {
    return this.device?.state === 'registered'
  }

  disconnect() {
    if (this.device) {
      this.device.unregister()
      this.device.destroy()
      this.device = null
    }
    this.activeCall = null
    this.onCallStatusChange?.('disconnected')
  }
}

export const twilioVoiceService = new TwilioVoiceService()