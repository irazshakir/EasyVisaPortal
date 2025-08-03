import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Header from '@/components/template/Header'

const HomeHeader = () => {
    const [logoLoaded, setLogoLoaded] = useState(false)

    useEffect(() => {
        // Test if logo file exists
        const testLogo = new Image()
        testLogo.onload = () => {
            console.log('Logo file exists and can be loaded')
            setLogoLoaded(true)
        }
        testLogo.onerror = () => {
            console.log('Logo file not found, using fallback')
            setLogoLoaded(false)
        }
        testLogo.src = '/img/logo/logo-light-full.svg'
    }, [])

    const headerStart = (
        <Link to="/" className="flex items-center pr-4">
            <div className="flex items-center">
                {logoLoaded ? (
                    <img 
                        src="/img/logo/logo-light-full.svg" 
                        alt="E-Visa Portal" 
                        className="h-8 sm:h-10 w-auto"
                    />
                ) : (
                    <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                            <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2h12v8H4V6z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <span className="text-xl font-bold text-gray-900 hidden sm:block">E-Visa Portal</span>
                    </div>
                )}
            </div>
        </Link>
    )

    const headerEnd = (
        <div className="flex items-center space-x-2 sm:space-x-4 pl-4">
            <Link to="/sign-in">
                <button className="px-3 sm:px-6 py-2 text-gray-600 hover:text-primary transition-colors font-medium text-sm sm:text-base">
                    Sign In
                </button>
            </Link>
            <Link to="/sign-up">
                <button className="px-3 sm:px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-deep transition-colors font-medium text-sm sm:text-base">
                    Get Started
                </button>
            </Link>
        </div>
    )

    return (
        <Header 
            className="bg-white shadow-sm"
            headerStart={headerStart}
            headerEnd={headerEnd}
        />
    )
}

export default HomeHeader 