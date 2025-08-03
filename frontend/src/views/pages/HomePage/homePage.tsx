import React from 'react'
import { Link } from 'react-router-dom'
import HomeHeader from './components/HomeHeader'
import HomeChatbox from './components/HomeChatbox'

const HomePage = () => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
            {/* Header */}
            <HomeHeader />

            {/* Chatbox Section */}
            <section className="py-20">
                <div className="container mx-auto px-4">
                    <div className="text-center mb-12">
                        <h2 className="text-4xl font-bold text-gray-900 mb-4">
                            Welcome to Easy Visa PK ! Online Visa Consultation
                        </h2>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                           Discuss your visa queries with our AI assistant.
                            Our AI assistant is here to help you 24/7.
                        </p>
                    </div>
                    
                    <HomeChatbox />
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-8">
                <div className="container mx-auto px-4 text-center">
                    <p>&copy; 2025 Easy Visa PK Portal. All rights reserved.</p>
                </div>
            </footer>
        </div>
    )
}

export default HomePage
