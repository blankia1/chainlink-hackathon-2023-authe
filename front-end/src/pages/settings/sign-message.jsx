import { useSignMessage } from 'wagmi'

export function SignMessage() {  
//   const recoveredAddress = React.useRef<string>()
  const { data, error, isLoading, signMessage, variables } = useSignMessage()

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        const formData = new FormData(event.target)
        const message = formData.get('message')
        signMessage({ message })
      }}
    >
      <label htmlFor="message">Enter a message to sign</label>
      <textarea
        id="message"
        name="message"
        placeholder="The quick brown fox…"
      />
      <button disabled={isLoading}>
        {isLoading ? 'Check Wallet' : 'Sign Message'}
      </button>

      {data && (
        <div>
          {/* <div>Recovered Address: {recoveredAddress.current}</div> */}
          <div>Signature: {data}</div>
        </div>
      )}

      {error && <div>{error.message}</div>}
    </form>
  )
}
