import { useSignMessage } from 'wagmi'
 
export function SignMessage() {
  const { data, error, isLoading, signMessage, variables } = useSignMessage()

  async function onClickFunction() {
    const message = "df"// formData.get('message')
    const result = await signMessage({ message })
  }

  return (
    <form
      // onSubmit={(event) => {
      //   event.preventDefault()
      //   const formData = new FormData(event.target)
      //   const message = "df"// formData.get('message')
      //   signMessage({ message })
      // }}
    >
      <button disabled={isLoading} onClick={onClickFunction} >
        {isLoading ? 'Check Wallet' : 'Sign Message'}
      </button>
 
      {data && (
        <div>
          {/* <div>Recovered Address: {recoveredAddress.current}</div> */}
          <div>Signature: {data}</div>
        </div>
      )}
     </form>
  )
}