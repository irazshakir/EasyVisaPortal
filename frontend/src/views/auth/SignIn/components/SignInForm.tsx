import { FormItem, FormContainer } from '@/components/ui/Form'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import Alert from '@/components/ui/Alert'
import { Field, Form, Formik } from 'formik'
import * as Yup from 'yup'
import useAuth from '@/auth/useAuth'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

type SignInFormProps = {
    disableSubmit?: boolean
    setMessage: (message: string) => void
    passwordHint?: React.ReactNode
}

type SignInFormSchema = {
    email: string
    password: string
}

const validationSchema = Yup.object().shape({
    email: Yup.string()
        .email('Please enter a valid email')
        .required('Email is required'),
    password: Yup.string()
        .min(6, 'Password must be at least 6 characters')
        .required('Password is required'),
})

const SignInForm = ({ disableSubmit, setMessage, passwordHint }: SignInFormProps) => {
    const { signIn } = useAuth()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)

    const initialValues = {
        email: '',
        password: '',
    }

    const handleSubmit = async (values: SignInFormSchema) => {
        setLoading(true)
        try {
            const result = await signIn(values)
            if (result.status === 'success') {
                navigate('/dashboard')
            } else {
                setMessage(result.message || 'Something went wrong')
            }
        } catch (error: any) {
            setMessage(error?.response?.data?.message || 'Failed to sign in')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <Formik
                initialValues={initialValues}
                validationSchema={validationSchema}
                onSubmit={handleSubmit}
                validateOnChange={true}
                validateOnBlur={true}
            >
                {({ touched, errors, isSubmitting }) => (
                    <Form>
                        <FormContainer>
                            <FormItem
                                label="Email"
                                invalid={Boolean(errors.email && touched.email)}
                                errorMessage={errors.email}
                            >
                                <Field
                                    type="email"
                                    name="email"
                                    placeholder="Email"
                                    component={Input}
                                    autoComplete="email"
                                />
                            </FormItem>
                            <FormItem
                                label="Password"
                                invalid={Boolean(errors.password && touched.password)}
                                errorMessage={errors.password}
                            >
                                <Field
                                    type="password"
                                    name="password"
                                    placeholder="Password"
                                    component={Input}
                                    autoComplete="current-password"
                                />
                            </FormItem>
                            {passwordHint}
                            <Button
                                block
                                loading={loading}
                                variant="solid"
                                type="submit"
                                disabled={disableSubmit || isSubmitting || loading}
                            >
                                {loading ? 'Signing in...' : 'Sign In'}
                            </Button>
                        </FormContainer>
                    </Form>
                )}
            </Formik>
        </div>
    )
}

export default SignInForm
