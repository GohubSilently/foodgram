import { Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  return (
    <Main>
      <MetaTags>
        <title>О проекте — Технологии</title>
        <meta name="description" content="Фудграм — Технологии и навыки" />
        <meta property="og:title" content="Технологии проекта Фудграм" />
      </MetaTags>

      <Container>
        <h1 className={styles.title}>Технологии</h1>
        <div className={styles.content}>

          <div>
            <h2 className={styles.subtitle}>Основные технологии и версии:</h2>
            <ul className={styles.text}>
              <li>Python 3.12</li>
              <li>Django 5.2.8</li>
              <li>Django REST Framework 3.16.1</li>
              <li>Djoser 2.3.3</li>
            </ul>
          </div>

          <div>
            <h2 className={styles.subtitle}>Основные навыки:</h2>
            <ul className={styles.text}>
              <li>REST API и аутентификация через JWT</li>
              <li>Работа с PostgreSQL</li>
              <li>Развёртывание через Docker и Nginx</li>
              <li>Обработка изображений с Pillow</li>
            </ul>
          </div>

        </div>
      </Container>
    </Main>
  )
}

export default Technologies


