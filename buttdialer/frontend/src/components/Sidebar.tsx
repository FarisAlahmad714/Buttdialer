import { NavLink } from 'react-router-dom'
import { 
  HomeIcon, 
  PhoneIcon, 
  UsersIcon, 
  UserGroupIcon,
  ShieldCheckIcon,
  Cog6ToothIcon 
} from '@heroicons/react/24/outline'
import { useAuthStore } from '../stores/authStore'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Calls', href: '/calls', icon: PhoneIcon },
  { name: 'Contacts', href: '/contacts', icon: UsersIcon },
  { name: 'Teams', href: '/teams', icon: UserGroupIcon },
  { name: 'Compliance', href: '/compliance', icon: ShieldCheckIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
]

export default function Sidebar() {
  const { user } = useAuthStore()

  return (
    <div className="hidden md:flex md:w-64 md:flex-col">
      <div className="flex flex-col flex-grow pt-5 pb-4 overflow-y-auto bg-white border-r border-gray-200">
        <div className="flex items-center flex-shrink-0 px-4">
          <PhoneIcon className="h-8 w-8 text-primary-600" />
          <span className="ml-2 text-xl font-bold text-gray-900">Buttdialer</span>
        </div>
        
        <div className="mt-5 flex-grow flex flex-col">
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                    isActive
                      ? 'bg-primary-100 text-primary-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`
                }
              >
                <item.icon className="mr-3 flex-shrink-0 h-5 w-5" />
                {item.name}
              </NavLink>
            ))}
          </nav>
        </div>
        
        <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
          <div className="flex-shrink-0 w-full group block">
            <div className="flex items-center">
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-700">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className="text-xs font-medium text-gray-500 capitalize">
                  {user?.role}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}